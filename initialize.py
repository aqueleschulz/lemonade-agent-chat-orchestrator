import subprocess, time, webbrowser, json, os, sys
from pathlib import Path

# Paths relativos ao layout pedido
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

# Importa config do backend
sys.path.insert(0, str(BACKEND_DIR))
from backend.config import (
    GAIA_BAT, GAIA_ARGS, GAIA_BASE,
    BACKEND_HOST, BACKEND_PORT, BACKEND_URL,
    FRONTEND_URL
)
from backend.app import serve as serve_backend

PROCS = []

def spawn(cmd: list[str], cwd: Path | None = None) -> subprocess.Popen:
    return subprocess.Popen(cmd, cwd=str(cwd or ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def start_gaia():
    # GAIA launcher (não bloqueante). Requer GAIA instalado com CLI.
    PROCS.append(spawn([GAIA_BAT, *GAIA_ARGS]))

def start_mcp_server():
    # Usa o Python da venv MCP, se existir; senão, usa o atual
    venv_python = ROOT / ".venv" / "Scripts" / "python.exe"
    py = str(venv_python if venv_python.exists() else sys.executable)
    # -u para STDIO sem buffer
    cmd = [py, "-u", "-m", "backend.mcp_server_fs"]
    # Armazenamos a *lista* para o client usar exatamente esses argumentos
    return cmd, spawn(cmd, cwd=ROOT)

def wait_port(url: str, tries=30, sleep_s=0.5):
    import requests
    for _ in range(tries):
        try:
            requests.get(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(sleep_s)
    return False

def main():
    print("[init] Launching GAIA…")
    start_gaia()

    print("[init] Launching MCP server (stdio)…")
    mcp_cmd, mcp_proc = start_mcp_server()
    PROCS.append(mcp_proc)

    # Esperar o GAIA responder antes de subir o backend
    print("[init] Waiting GAIA…")
    wait_port(f"{GAIA_BASE}", tries=20, sleep_s=0.5)

    print("[init] Starting backend…")
    # Rodar o backend no mesmo processo para facilitar Ctrl+C
    # passa MCP_CMD (lista) para o app
    import threading
    t = threading.Thread(target=serve_backend, args=("127.0.0.1", BACKEND_PORT, mcp_cmd), daemon=True)
    t.start()

    # Abre o front
    index = (FRONTEND_DIR / "index.html").as_uri()
    print(f"[init] Opening UI: {index}")
    webbrowser.open(index)

    print("[init] Ready.")
    t.join()

if __name__ == "__main__":
    try:
        main()
    finally:
        for p in PROCS:
            if p and p.poll() is None:
                p.terminate()
