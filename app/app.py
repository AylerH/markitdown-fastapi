import os
import uuid
import logging
import shutil
from pathlib import Path
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路径计算
# __file__ 是 app/app.py，其 parent 是 app/ 文件夹
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
# 数据目录建议放在根级或容器指定的持久化路径
UPLOAD_DIR = Path("/app/uploads")
CONVERTED_DIR = Path("/app/converted")

# 确保目录存在
for d in [UPLOAD_DIR, CONVERTED_DIR, STATIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# 打印路径调试信息 (启动时可见)
logger.info(f"Checking STATIC_DIR: {STATIC_DIR} | Exists: {STATIC_DIR.exists()}")

md_converter = MarkItDown(enable_plugins=False)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding='utf-8')
    return f"<h1>404: static/index.html not found</h1><p>Expected path: {index_path}</p>"

@app.post("/convert-multiple")
async def convert_multiple_files(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.filename: continue
        
        unique_id = str(uuid.uuid4())[:8]
        safe_name = os.path.basename(file.filename)
        temp_path = UPLOAD_DIR / f"{unique_id}_{safe_name}"
        
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Converting: {safe_name}")
            res = md_converter.convert(str(temp_path))
            
            md_name = f"{Path(safe_name).stem}_{unique_id}.md"
            out_path = CONVERTED_DIR / md_name
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(res.text_content)
            
            results.append({
                "filename": safe_name,
                "status": "success",
                "download_url": f"/download/{md_name}"
            })
        except Exception as e:
            logger.error(f"Error {safe_name}: {str(e)}")
            results.append({"filename": safe_name, "status": "error", "message": str(e)})
        finally:
            if temp_path.exists(): temp_path.unlink()
            
    return {"results": results}

@app.get("/download/{filename}")
async def download(filename: str):
    path = CONVERTED_DIR / filename
    if not path.exists(): raise HTTPException(status_code=404)
    return FileResponse(path=str(path), filename=filename, media_type='text/markdown')

@app.get("/health")
def health():
    return {"static_exists": (STATIC_DIR / "index.html").exists(), "static_path": str(STATIC_DIR)}