from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF for PDFs

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Handle by extension
    if file.filename.endswith(".txt"):
        text = contents.decode("utf-8", errors="ignore")

    elif file.filename.endswith(".pdf"):
        text = ""
        with fitz.open(stream=contents, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()

    elif file.filename.endswith(".csv"):
        text = contents.decode("utf-8", errors="ignore")
        # optionally parse with pandas

    else:
        return JSONResponse({"reply": "Unsupported file type."}, status_code=400)

    # For now, just return a preview
    preview = text[:300] + ("..." if len(text) > 300 else "")
    return {"reply": f"I’ve read your file '{file.filename}'. Preview:\n{preview}"}
