import asyncio
from pathlib import Path
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from markitdown import MarkItDown

from .config import DRIVE_ROOT

# Aviso do DEV: JAMAIS usar print()/stdout aqui (STDIO é o transporte do protocolo)
server = Server("fs-context")


# utilitário seguro de extração
def _extract_text(p: Path, max_bytes: int) -> str:
    """
    Extrair texto usando MarkItDown.
    Se falhar, retorna erro explícito em vez de ler binário bruto.
    """
    try:
        md = MarkItDown()
        result = md.convert(str(p))
        text = result.text_content.strip()
        return text[:max_bytes] if text else "(Arquivo sem conteúdo legível)"
    except Exception as e:
        
        # Listar extensões seguras para leitura bruta se o MarkItDown falhar
        SAFE_TEXT_EXTS = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.log', '.csv'}
        
        if p.suffix.lower() in SAFE_TEXT_EXTS:
            try:
                data = p.read_bytes()[:max_bytes]
                return data.decode("utf-8", errors="ignore")
            except Exception:
                pass
        
        # Retornar o erro da conversão
        return f"(Erro na conversão do arquivo {p.name}: {str(e)})"


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_files",
            description="Lista arquivos recursivamente a partir do DRIVE_ROOT",
            inputSchema={
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": [],
            },
        ),
        types.Tool(
            name="read_file",
            description="Lê o conteúdo de um arquivo (txt, docx, pdf, xlsx, odt, etc.) usando MarkItDown",
            inputSchema={
                "type": "object",
                "properties": {
                    "relpath": {"type": "string"},
                    "max_bytes": {"type": "number"},
                },
                "required": ["relpath"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    root = DRIVE_ROOT.resolve()

    if name == "list_files":
        pattern = (arguments.get("pattern") or "**/*").strip() or "**/*"
        files = [str(p.relative_to(root)) for p in root.glob(pattern) if p.is_file()]
        return [types.TextContent(type="text", text="\n".join(files))]

    if name == "read_file":
        relpath = arguments["relpath"]
        max_bytes = int(arguments.get("max_bytes") or 2097152)
        p = (root / relpath).resolve()

        # evitar path traversal
        if not str(p).startswith(str(root)):
            return [types.TextContent(type="text", text="Path fora do DRIVE_ROOT")]

        if not p.exists():
            return [types.TextContent(type="text", text=f"Arquivo não encontrado: {relpath}")]

        text = _extract_text(p, max_bytes)
        return [types.TextContent(type="text", text=text)]

    return [types.TextContent(type="text", text=f"tool desconhecida: {name}")]


async def _run():
    # abrir STDIO como context manager e rodar o servidor
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fs-context",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()
