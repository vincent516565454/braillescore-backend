from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid

app = FastAPI()

# CORS pour le frontend local
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://braillescore-frontend-production.up.railway.app",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
UPLOADS = BASE_DIR / "uploads"
OUTPUTS = BASE_DIR / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    suffix = Path(file.filename).suffix.lower()
    in_path = UPLOADS / f"{job_id}{suffix}"
    content = await file.read()
    in_path.write_bytes(content)

    out_path = OUTPUTS / f"{job_id}.brf"
    brf_text = (
        "BRAILLESCORE DEMO OUTPUT\n"
        f"Original filename: {file.filename}\n"
        "Status: Converted (stub)\n"
    )
    out_path.write_text(brf_text, encoding="utf-8")

    return {"job_id": job_id, "download_url": f"/download/{job_id}"}

@app.get("/download/{job_id}")
def download(job_id: str):
    out_path = OUTPUTS / f"{job_id}.brf"
    if not out_path.exists():
        return {"error": "Not found"}
    return FileResponse(
        path=str(out_path),
        media_type="application/octet-stream",
        filename=f"{job_id}.brf",
    )
