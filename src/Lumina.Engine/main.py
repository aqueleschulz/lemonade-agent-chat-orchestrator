from config import DRIVE_ROOT
from fastapi import FastAPI, UploadFile, File, HTTPException
from markitdown import MarkItDown
import shutil
import os
import tempfile

app = FastAPI(title="Lumina Engine (Python)", description="A simple API to convert files to text content using MarkItDown.", version="1.0.0")
md = MarkItDown()

@app.get("/health")
def health_check():
    return {"status": "operational", "service": "Lumina Engine (Python)"}

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        result = md.convert(temp_path)
        
        os.remove(temp_path)
        
        return {
            "filename": file.filename,
            "content": result.text_content
        }

    except Exception as e:
        return HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

@app.get("/tools/list-files")
async def list_files():
    files = []
    for file in DRIVE_ROOT.iterdir():
        if file.is_file():
            files.append(file.name)
    return {"files": files}

@app.post("/tools/read-file")
async def read_file(filename: str):
    file_path = DRIVE_ROOT / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = md.convert(file_path)
        return {"content": result.text_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001)