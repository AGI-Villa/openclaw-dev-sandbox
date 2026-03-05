"""
Web server for background removal tool using rembg's built-in HTTP server.
"""
import os
import sys
import json
import uuid
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to Python path to import core module
sys.path.insert(0, str(Path(__file__).parent.parent))

from bg_removal.core import remove_background
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import tempfile

app = FastAPI(title="Background Removal API")

# 历史记录存储配置
DATA_DIR = Path("/data")
HISTORY_FILE = DATA_DIR / "history.json"
PROCESSED_DIR = DATA_DIR / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 历史记录数量限制
MAX_HISTORY_RECORDS = 100

# 初始化历史记录文件
if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]")

def load_history():
    """加载历史记录"""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info("History file not found, creating new history")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"History file JSON decode error: {e}")
        # 备份损坏的文件
        backup_file = HISTORY_FILE.with_suffix('.json.corrupted')
        try:
            shutil.copy2(HISTORY_FILE, backup_file)
            logger.warning(f"Corrupted history file backed up to {backup_file}")
        except Exception as backup_err:
            logger.error(f"Failed to backup corrupted history file: {backup_err}")
        return []

def save_history(history):
    """保存历史记录"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save history: {e}")
        raise

def add_history_record(original_filename, processed_filename, file_size):
    """添加历史记录"""
    history = load_history()
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "original_filename": original_filename,
        "processed_filename": processed_filename,
        "file_size": file_size
    }
    history.insert(0, record)  # 最新的在前面

    # 限制历史记录数量
    if len(history) > MAX_HISTORY_RECORDS:
        removed = history[MAX_HISTORY_RECORDS:]
        history = history[:MAX_HISTORY_RECORDS]
        # 删除超出的记录对应的文件
        for r in removed:
            processed_path = PROCESSED_DIR / r["processed_filename"]
            if processed_path.exists():
                try:
                    processed_path.unlink()
                    logger.info(f"Removed old processed file: {r['processed_filename']}")
                except Exception as e:
                    logger.error(f"Failed to remove old file {r['processed_filename']}: {e}")

    save_history(history)
    return record

def delete_history_record(record_id):
    """删除历史记录及对应的图片文件"""
    history = load_history()
    record = next((r for r in history if r["id"] == record_id), None)
    if record:
        # 删除处理后的图片文件
        processed_path = PROCESSED_DIR / record["processed_filename"]
        if processed_path.exists():
            processed_path.unlink()
        # 从历史记录中移除
        history = [r for r in history if r["id"] != record_id]
        save_history(history)
        return True
    return False

# Mount static files (web interface)
static_dir = Path(__file__).parent / "web"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def read_root():
    """Serve the main web page"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(status_code=404, detail="Web interface not found")

@app.post("/api/remove-bg")
async def remove_background_api(file: UploadFile = File(...)):
    """
    Remove background from uploaded image file.

    Args:
        file: Uploaded image file (PNG, JPG, or WebP)

    Returns:
        Processed image with transparent background as PNG
    """
    # Validate file type
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in valid_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported types: {', '.join(valid_extensions)}"
        )

    # Validate file size (10MB limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # 生成唯一的输出文件名
    output_filename = f"{uuid.uuid4()}.png"
    output_path = PROCESSED_DIR / output_filename

    # 保存上传的文件到临时位置
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_input:
        shutil.copyfileobj(file.file, temp_input)
        temp_input_path = temp_input.name

    try:
        # 处理图片 - 注意 remove_background 需要 input 和 output 两个参数
        output_path = remove_background(temp_input_path, output_path)

        # 保存到历史记录
        add_history_record(
            original_filename=file.filename,
            processed_filename=output_filename,
            file_size=file_size
        )

        # 返回处理后的图片
        def iterfile():
            with open(output_path, "rb") as f:
                yield from f

        return StreamingResponse(
            iterfile(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=background-removed.png"}
        )
    finally:
        # 清理临时输入文件（处理后的文件保留在 /data/processed/）
        if os.path.exists(temp_input_path):
            os.unlink(temp_input_path)


@app.get("/api/history")
async def get_history():
    """获取历史记录列表"""
    history = load_history()

    # 添加文件大小的人类可读格式和下载 URL
    for record in history:
        record["file_size_human"] = format_file_size(record["file_size"])
        record["download_url"] = f"/api/download/{record['processed_filename']}"

    return {"history": history}


@app.delete("/api/history/{record_id}")
async def delete_history(record_id: str):
    """删除指定历史记录"""
    # 验证 record_id 是否为有效的 UUID 格式
    try:
        uuid.UUID(record_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid record ID format. Must be a valid UUID.")

    success = delete_history_record(record_id)
    if success:
        return {"message": "Deleted successfully"}
    raise HTTPException(status_code=404, detail="Record not found")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载处理后的图片"""
    file_path = PROCESSED_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        media_type="image/png",
        filename=f"background-removed-{filename[:8]}.png"
    )


@app.delete("/api/history")
async def clear_all_history():
    """清空所有历史记录（批量删除）"""
    try:
        history = load_history()
        # 删除所有处理后的图片文件
        for record in history:
            processed_path = PROCESSED_DIR / record["processed_filename"]
            if processed_path.exists():
                try:
                    processed_path.unlink()
                    logger.info(f"Removed processed file: {record['processed_filename']}")
                except Exception as e:
                    logger.error(f"Failed to remove file {record['processed_filename']}: {e}")
        # 清空历史记录
        save_history([])
        logger.info("All history cleared successfully")
        return {"message": "All history cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear history: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear history")


def format_file_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def start_web_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the web server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_web_server()
