#!/usr/bin/env python3
"""
YouTube to MP3 API Server
API service để tải và chuyển đổi YouTube sang MP3
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import yt_dlp
import uvicorn

# Khởi tạo FastAPI app
app = FastAPI(
    title="YouTube to MP3 Converter API",
    description="API để tải video YouTube và chuyển đổi sang MP3",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thư mục lưu file
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Lưu trạng thái các task
tasks_status = {}


class DownloadRequest(BaseModel):
    """Model cho request download"""
    url: HttpUrl
    no_check_certificate: bool = False


class DownloadResponse(BaseModel):
    """Model cho response download"""
    task_id: str
    status: str
    message: str


class TaskStatus(BaseModel):
    """Model cho trạng thái task"""
    task_id: str
    status: str
    progress: int
    title: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
    created_at: str


def download_youtube_mp3(url: str, task_id: str, no_check_certificate: bool = False):
    """
    Tải video YouTube và chuyển đổi sang MP3

    Args:
        url: YouTube URL
        task_id: ID của task
        no_check_certificate: Bỏ qua SSL verification
    """
    try:
        # Update status: đang tải
        tasks_status[task_id]["status"] = "downloading"
        tasks_status[task_id]["progress"] = 10

        # Cấu hình yt-dlp
        output_template = str(DOWNLOADS_DIR / f"{task_id}_%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: update_progress(d, task_id)],
        }

        if no_check_certificate:
            ydl_opts['nocheckcertificate'] = True

        # Tải và chuyển đổi
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown')

            tasks_status[task_id]["title"] = video_title
            tasks_status[task_id]["progress"] = 90

            # Tìm file MP3 đã tải
            mp3_files = list(DOWNLOADS_DIR.glob(f"{task_id}_*.mp3"))

            if mp3_files:
                file_path = str(mp3_files[0])
                tasks_status[task_id]["status"] = "completed"
                tasks_status[task_id]["progress"] = 100
                tasks_status[task_id]["file_path"] = file_path
            else:
                raise Exception("Không tìm thấy file MP3 sau khi chuyển đổi")

    except Exception as e:
        tasks_status[task_id]["status"] = "failed"
        tasks_status[task_id]["error"] = str(e)
        tasks_status[task_id]["progress"] = 0


def update_progress(d, task_id):
    """Cập nhật tiến độ download"""
    if d['status'] == 'downloading':
        if 'downloaded_bytes' in d and 'total_bytes' in d:
            progress = int(d['downloaded_bytes'] / d['total_bytes'] * 80) + 10
            tasks_status[task_id]["progress"] = progress
    elif d['status'] == 'finished':
        tasks_status[task_id]["progress"] = 85


@app.get("/")
async def root():
    """Endpoint gốc"""
    return {
        "message": "YouTube to MP3 Converter API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/download", response_model=DownloadResponse)
async def download_video(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    Tải video YouTube và chuyển đổi sang MP3

    Args:
        request: DownloadRequest với URL và options
        background_tasks: FastAPI BackgroundTasks

    Returns:
        DownloadResponse với task_id để theo dõi tiến độ
    """
    # Tạo task ID
    task_id = str(uuid.uuid4())

    # Khởi tạo trạng thái task
    tasks_status[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "title": None,
        "file_path": None,
        "error": None,
        "created_at": datetime.now().isoformat()
    }

    # Thêm task vào background
    background_tasks.add_task(
        download_youtube_mp3,
        str(request.url),
        task_id,
        request.no_check_certificate
    )

    return DownloadResponse(
        task_id=task_id,
        status="pending",
        message="Download task đã được tạo. Sử dụng task_id để kiểm tra tiến độ."
    )


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    """
    Kiểm tra trạng thái của task

    Args:
        task_id: ID của task

    Returns:
        TaskStatus với thông tin chi tiết
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task không tồn tại")

    return TaskStatus(**tasks_status[task_id])


@app.get("/download/{task_id}")
async def download_file(task_id: str):
    """
    Tải file MP3 về

    Args:
        task_id: ID của task

    Returns:
        File MP3
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task không tồn tại")

    task = tasks_status[task_id]

    if task["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Task chưa hoàn thành. Trạng thái: {task['status']}"
        )

    file_path = task["file_path"]

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File không tồn tại")

    filename = os.path.basename(file_path)

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )


@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """
    Xóa task và file liên quan

    Args:
        task_id: ID của task

    Returns:
        Thông báo xóa thành công
    """
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task không tồn tại")

    task = tasks_status[task_id]

    # Xóa file nếu có
    if task["file_path"] and os.path.exists(task["file_path"]):
        os.remove(task["file_path"])

    # Xóa task khỏi dictionary
    del tasks_status[task_id]

    return {"message": "Task đã được xóa thành công"}


@app.get("/tasks")
async def list_tasks():
    """
    Liệt kê tất cả tasks

    Returns:
        Dictionary của tất cả tasks
    """
    return {"tasks": list(tasks_status.values())}


if __name__ == "__main__":
    # Chạy server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
