"""
Web server for background removal tool using rembg's built-in HTTP server.
"""
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import core module
sys.path.insert(0, str(Path(__file__).parent.parent))

from bg_removal.core import remove_background_from_file
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import tempfile
import shutil

app = FastAPI(title="Background Removal API")

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
async def remove_background(file: UploadFile = File(...)):
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
    
    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_input:
        # Save uploaded file
        shutil.copyfileobj(file.file, temp_input)
        temp_input_path = temp_input.name
    
    try:
        # Process the image
        output_path = remove_background_from_file(temp_input_path)
        
        # Return the processed image
        def iterfile():
            with open(output_path, "rb") as f:
                yield from f
        
        return StreamingResponse(
            iterfile(), 
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=background-removed.png"}
        )
    finally:
        # Clean up temporary files
        if os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.unlink(output_path)

def start_web_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the web server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_web_server()