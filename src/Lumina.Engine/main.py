from config import DRIVE_ROOT, CHROMA_PATH
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from markitdown import MarkItDown
from pydantic import BaseModel
import shutil, os, re, tempfile
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

app = FastAPI(
    title="Lumina Engine (Python)",
    description="Motor de ETL e RAG do Lumina Orchestrator — converte ficheiros, indexa e faz busca semântica.",
    version="2.0.0",
)

md = MarkItDown()

_chroma = chromadb.PersistentClient(path=str(CHROMA_PATH))
_embed_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
_collection = _chroma.get_or_create_collection(name="lumina_docs", embedding_function=_embed_fn)


def _safe_resolve(filename: str) -> "os.PathLike":
    try:
        resolved = (DRIVE_ROOT / filename).resolve()
        resolved.relative_to(DRIVE_ROOT)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Acesso negado: o caminho '{filename}' está fora do diretório permitido.",
        )
    return resolved


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[i : i + chunk_size])
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks

@app.get("/health")
def health_check():
    return {"status": "operational", "service": "Lumina Engine (Python)", "drive_root": str(DRIVE_ROOT)}


@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename or "")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        try:
            result = md.convert(tmp_path)
        finally:
            os.remove(tmp_path)
        return {"filename": file.filename, "content": result.text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {e}")

@app.get("/tools/list-files")
async def list_files():
    try:
        files = [f.name for f in DRIVE_ROOT.iterdir() if f.is_file()]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar ficheiros: {e}")


@app.post("/tools/read-file")
async def read_file(filename: str = Query(..., description="Nome do ficheiro com extensão")):
    file_path = _safe_resolve(filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Ficheiro '{filename}' não encontrado.")

    try:
        result = md.convert(str(file_path))
        return {"filename": filename, "content": result.text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler ficheiro: {e}")

class IngestResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str


@app.post("/tools/ingest-file", response_model=IngestResponse)
async def ingest_file(filename: str = Query(..., description="Nome do ficheiro a indexar")):
    file_path = _safe_resolve(filename)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Ficheiro '{filename}' não encontrado.")

    try:
        result = md.convert(str(file_path))
        text = result.text_content or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao converter ficheiro: {e}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="O ficheiro não gerou conteúdo de texto.")

    chunks = _chunk_text(text)

    existing = _collection.get(where={"source": filename})
    if existing["ids"]:
        _collection.delete(ids=existing["ids"])

    ids = [f"{filename}::chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

    _collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    return IngestResponse(
        filename=filename,
        chunks_indexed=len(chunks),
        message=f"'{filename}' indexado com sucesso em {len(chunks)} chunk(s).",
    )


class SearchRequest(BaseModel):
    query: str
    filename: str | None = None
    top_k: int = 4


class SearchResult(BaseModel):
    source: str
    chunk_index: int
    content: str
    distance: float


@app.post("/tools/search", response_model=list[SearchResult])
async def semantic_search(req: SearchRequest):
    if _collection.count() == 0:
        raise HTTPException(
            status_code=404,
            detail="Nenhum documento indexado. Use /tools/ingest-file primeiro.",
        )

    where_filter = {"source": req.filename} if req.filename else None

    try:
        results = _collection.query(
            query_texts=[req.query],
            n_results=min(req.top_k, _collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca semântica: {e}")

    output: list[SearchResult] = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, dists):
        output.append(
            SearchResult(
                source=meta.get("source", "unknown"),
                chunk_index=meta.get("chunk_index", 0),
                content=doc,
                distance=round(dist, 4),
            )
        )

    return output

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
