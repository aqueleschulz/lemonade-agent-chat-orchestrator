# backend/mcp_client.py
import asyncio
import re
from collections import Counter
from contextlib import asynccontextmanager
from typing import Iterable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import MAX_BYTES_PER_SNIPPET, MAX_CONTEXT_SNIPPETS

TEXT_EXTS = (
    ".txt", ".md", ".markdown", ".rst",
    ".json", ".csv", ".tsv", ".log",
    ".yaml", ".yml", ".xml", ".ini", ".cfg",
    ".py", ".js", ".ts", ".java", ".cs", ".c", ".cpp", ".html", ".css"
)

@asynccontextmanager
async def connect(mcp_cmd: list[str]):
    params = StdioServerParameters(command=mcp_cmd[0], args=mcp_cmd[1:])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

def _tokenize(text: str) -> list[str]:
    # letras, números, underscore, hífen e ponto (pra preservar "nomes.txt")
    return [t for t in re.split(r"[^a-z0-9._-]+", text.lower()) if t]

def _extract_filenames_from_query(tokens: list[str]) -> set[str]:
    # pegar tokens que parecem nomes de arquivo (tem ponto + extensão)
    files = set()
    for t in tokens:
        if "." in t and len(t) > 2 and not t.endswith("."):
            files.add(t)
    return files

def _score_by_keywords(filename: str, keywords: Iterable[str]) -> int:
    f = filename.lower()
    # contar quantos keywords aparecem no nome do arquivo
    return sum(1 for kw in keywords if kw and kw in f)

async def _list_files(session: ClientSession) -> list[str]:
    tools = await session.list_tools()
    has_list = any(t.name == "list_files" for t in tools.tools)
    if not has_list:
        return []
    listed = await session.call_tool("list_files", {})
    files_txt = "".join([getattr(c, "text", "") for c in listed.content if getattr(c, "text", None)])
    files = [f.strip() for f in files_txt.splitlines() if f.strip()]
    return files

async def _read_file(session: ClientSession, rel: str, max_bytes: int) -> str:
    res = await session.call_tool("read_file", {"relpath": rel, "max_bytes": max_bytes})
    return "".join([getattr(c, "text", "") for c in res.content if getattr(c, "text", None)])

async def collect_context(session: ClientSession, query: str) -> tuple[list[str], list[str]]:
    """
    Selecionar até MAX_CONTEXT_SNIPPETS arquivos da raiz MCP, ler até MAX_BYTES_PER_SNIPPET de cada,
    e retornar (trechos, citations).
    """
    tools = await session.list_tools()
    if not any(t.name == "read_file" for t in tools.tools):
        return [], []

    files = await _list_files(session)
    if not files:
        return [], []

    tokens = _tokenize(query)
    mention_files = _extract_filenames_from_query(tokens)

    # Se a pergunta menciona arquivos explicitamente
    explicit = []
    if mention_files:
        lowered = {f.lower(): f for f in files}
        for mf in mention_files:
            # tentar casar nomes exatos; se não, casa por "termina com" (ex.: "docs/nomes.txt")
            if mf in lowered:
                explicit.append(lowered[mf])
            else:
                for real in files:
                    if real.lower().endswith(mf):
                        explicit.append(real)
                        break

    # Se não houver menções explícitas, classificar por overlap de palavras-chave
    ranked = []
    if not explicit:
        # keywords = tokens "significativos" (remova palavras comuns)
        stop = {"o","a","os","as","um","uma","de","do","da","dos","das","no","na","nos","nas","em",
                "como","que","qual","quais","para","por","no","na","sobre","arquivo","arquivos"}
        keywords = [t for t in tokens if t not in stop and len(t) > 2]
        # pontuar
        for f in files:
            score = _score_by_keywords(f, keywords)
            # leve bônus se for extensão textual
            if f.lower().endswith(TEXT_EXTS):
                score += 1
            if score > 0:
                ranked.append((score, f))
        ranked.sort(key=lambda x: (-x[0], x[1]))

    # Pegar arquivos de texto “top N” se nada casou
    candidates: list[str] = []
    if explicit:
        candidates = explicit[:MAX_CONTEXT_SNIPPETS]
    elif ranked:
        candidates = [f for _, f in ranked[:MAX_CONTEXT_SNIPPETS]]
    else:
        candidates = [f for f in files if f.lower().endswith(TEXT_EXTS)][:MAX_CONTEXT_SNIPPETS]

    snippets, cites = [], []
    for rel in candidates:
        try:
            text = (await _read_file(session, rel, MAX_BYTES_PER_SNIPPET)).strip()
            if text:
                snippets.append(f"[{rel}]\n{text}")
                cites.append(rel)
        except Exception:
            # ignorar arquivo problemático
            continue

    return snippets, cites

def gather_snippets(mcp_cmd: list[str], query: str):
    return asyncio.run(_gather(mcp_cmd, query))

async def _gather(mcp_cmd, query):
    async with connect(mcp_cmd) as session:
        return await collect_context(session, query)
