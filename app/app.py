import os
import uuid
import logging
import shutil
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, StreamingResponse
from markitdown import MarkItDown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MarkItDown Multi-Task API")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = Path("/app/uploads")
CONVERTED_ROOT = Path("/app/converted")

# 初始化必要目录
for d in [UPLOAD_DIR, CONVERTED_ROOT, STATIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)
(CONVERTED_ROOT / "default").mkdir(exist_ok=True)

md_converter = MarkItDown(enable_plugins=False)

def get_task_dir(task_name: str) -> Path:
    safe_name = "".join([c for c in task_name if c.isalnum() or c in ('-', '_')]).strip()
    if not safe_name: safe_name = "default"
    path = CONVERTED_ROOT / safe_name
    path.mkdir(exist_ok=True)
    return path

@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = STATIC_DIR / "index.html"
    return index_path.read_text(encoding='utf-8') if index_path.exists() else "<h1>index.html not found</h1>"

@app.post("/convert")
async def convert_files(files: List[UploadFile] = File(...), task_name: str = Form("default")):
    task_dir = get_task_dir(task_name)
    results = []
    for file in files:
        if not file.filename: continue
        uid = str(uuid.uuid4())[:6]
        safe_name = os.path.basename(file.filename)
        temp_path = UPLOAD_DIR / f"{uid}_{safe_name}"
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            res = md_converter.convert(str(temp_path))
            md_name = f"{Path(safe_name).stem}_{uid}.md"
            with open(task_dir / md_name, "w", encoding="utf-8") as f:
                f.write(res.text_content)
            results.append({"filename": safe_name, "status": "success"})
        except Exception as e:
            results.append({"filename": safe_name, "status": "error", "message": str(e)})
        finally:
            if temp_path.exists(): temp_path.unlink()
    return {"status": "done", "results": results}

@app.get("/list-tasks")
async def list_tasks():
    tasks = []
    for d in CONVERTED_ROOT.iterdir():
        if d.is_dir():
            files = [{"name": f.name, "size": f.stat().st_size} for f in d.glob("*.md")]
            tasks.append({"name": d.name, "files": files})
    return sorted(tasks, key=lambda x: x['name'])

@app.get("/download-zip/{task_name}")
async def download_zip(task_name: str):
    task_dir = CONVERTED_ROOT / task_name
    files = list(task_dir.glob("*.md"))
    if not files: raise HTTPException(status_code=404)
    io_buf = BytesIO()
    with zipfile.ZipFile(io_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files: zf.write(f, arcname=f.name)
    io_buf.seek(0)
    return StreamingResponse(io_buf, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={task_name}.zip"})

@app.get("/download-single/{task_name}/{filename}")
async def download_single(task_name: str, filename: str):
    return FileResponse(path=CONVERTED_ROOT / task_name / filename, filename=filename)

@app.delete("/delete-file/{task_name}/{filename}")
async def delete_file(task_name: str, filename: str):
    p = CONVERTED_ROOT / task_name / filename
    if p.exists(): p.unlink()
    return {"status": "ok"}

@app.delete("/delete-task/{task_name}")
async def delete_task(task_name: str):
    task_dir = CONVERTED_ROOT / task_name
    if task_dir.exists():
        shutil.rmtree(task_dir)
        if task_name == "default": task_dir.mkdir()
    return {"status": "ok"}

@app.delete("/clear-all")
async def clear_all():
    for d in CONVERTED_ROOT.iterdir():
        if d.is_dir(): shutil.rmtree(d)
    (CONVERTED_ROOT / "default").mkdir()
    return {"status": "ok"}