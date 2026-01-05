from pathlib import Path

# Caminhos e endpoints fornecidos
GAIA_BAT = r"C:\Users\User\AppData\Local\GAIA\bin\launch_gaia.bat"
GAIA_ARGS = ["--cli"]  # CLI headless
GAIA_BASE = "http://localhost:8000"  # GAIA server base
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8080
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
FRONTEND_URL = "http://localhost:5500"

# Raiz de contexto do MCP
DRIVE_ROOT = Path(r"C:\Users\User\Documents\CloudDrive")

# LLM defaults
GAIA_MODEL = "Gemma-3-4b-it-GGUF" # O cliente pode escolher a IA que quiser
REQUEST_TIMEOUT_SEC = 60  # timeout de rede
MAX_CONTEXT_SNIPPETS = 2
MAX_BYTES_PER_SNIPPET = 2000
