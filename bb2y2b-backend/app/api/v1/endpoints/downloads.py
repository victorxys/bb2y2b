"""
下载任务管理API端点
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import os
import re
from sqlalchemy.orm import Session

from app.services.download_manager import download_manager, TaskStatus
from app.core.database import get_db
from app.models.video import Video

router = APIRouter()

# 项目根目录 (bb2y2b-backend 的父目录)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
VIDEO_OUTPUT_PATH = PROJECT_ROOT / 'video'
COVER_OUTPUT_PATH = PROJECT_ROOT / 'cover'
SUBTITLE_OUTPUT_PATH = PROJECT_ROOT / 'srt'

# 如果路径不存在，尝试使用相对于当前工作目录的路径
if not VIDEO_OUTPUT_PATH.exists():
    # 尝试从工作目录查找
    cwd = Path(os.getcwd())
    if (cwd.parent / 'video').exists():
        VIDEO_OUTPUT_PATH = cwd.parent / 'video'
        COVER_OUTPUT_PATH = cwd.parent / 'cover'
        SUBTITLE_OUTPUT_PATH = cwd.parent / 'srt'
    elif (cwd / 'video').exists():
        VIDEO_OUTPUT_PATH = cwd / 'video'
        COVER_OUTPUT_PATH = cwd / 'cover'
        SUBTITLE_OUTPUT_PATH = cwd / 'srt'


def _extract_bvid_from_filename(filename: str) -> Optional[str]:
    """从文件名提取bvid，格式如 BV1eemEBfEXq_1_1.mp3"""
    match = re.match(r'^(BV[a-zA-Z0-9]+)', filename)
    return match.group(1) if match else None


@router.get("/tasks")
async def get_all_tasks():
    """获取所有下载任务"""
    tasks = download_manager.get_all_tasks()
    return {
        "tasks": tasks,
        "total": len(tasks)
    }


@router.get("/tasks/active")
async def get_active_tasks():
    """获取活跃的下载任务（下载中/合并中）"""
    tasks = download_manager.get_active_tasks()
    return {
        "tasks": tasks,
        "total": len(tasks)
    }


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """获取指定任务的详情"""
    task = download_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.get("/tasks/bvid/{bvid}")
async def get_task_by_bvid(bvid: str):
    """根据bvid获取最新任务"""
    task = download_manager.get_task_by_bvid(bvid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@router.delete("/tasks/{task_id}")
async def remove_task(task_id: str):
    """移除任务记录"""
    download_manager.remove_task(task_id)
    return {"message": "Task removed"}


@router.post("/tasks/clear-completed")
async def clear_completed_tasks():
    """清除已完成的任务"""
    download_manager.clear_completed()
    return {"message": "Completed tasks cleared"}


@router.get("/files")
async def list_downloaded_files(db: Session = Depends(get_db)):
    """列出已下载的文件"""
    files = []
    
    # 扫描视频/音频目录
    if VIDEO_OUTPUT_PATH.exists():
        for f in VIDEO_OUTPUT_PATH.iterdir():
            if f.is_file() and f.suffix in ['.mp3', '.mp4', '.m4a']:
                stat = f.stat()
                # 尝试找到对应的封面和字幕
                cover_name = f.stem + '.jpg'
                cover_path = COVER_OUTPUT_PATH / cover_name
                subtitle_name = f.stem + '.txt'
                subtitle_path = SUBTITLE_OUTPUT_PATH / subtitle_name
                
                # 从文件名提取bvid并查询数据库获取标题
                bvid = _extract_bvid_from_filename(f.name)
                title = None
                if bvid:
                    video = db.query(Video).filter(Video.bvid == bvid).first()
                    if video:
                        title = video.title
                
                files.append({
                    "name": f.name,
                    "path": str(f),
                    "size": stat.st_size,
                    "size_formatted": _format_size(stat.st_size),
                    "created_at": stat.st_ctime,
                    "type": f.suffix[1:],
                    "bvid": bvid,
                    "title": title,
                    "cover_path": str(cover_path) if cover_path.exists() else None,
                    "cover_url": f"/api/v1/downloads/cover/{cover_name}" if cover_path.exists() else None,
                    "subtitle_path": str(subtitle_path) if subtitle_path.exists() else None,
                    "has_subtitle": subtitle_path.exists()
                })
    
    # 按创建时间倒序排列
    files.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {
        "files": files,
        "total": len(files)
    }


@router.get("/file/{filename}")
async def get_file(filename: str):
    """获取下载的文件"""
    file_path = VIDEO_OUTPUT_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/stream/{filename}")
async def stream_file(filename: str, request: Request):
    """流媒体播放文件，支持Range请求"""
    file_path = VIDEO_OUTPUT_PATH / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    file_size = file_path.stat().st_size
    
    # 根据文件类型设置MIME类型
    suffix = file_path.suffix.lower()
    media_types = {
        '.mp3': 'audio/mpeg',
        '.mp4': 'video/mp4',
        '.m4a': 'audio/mp4',
        '.webm': 'video/webm',
    }
    media_type = media_types.get(suffix, 'application/octet-stream')
    
    # 解析Range头
    range_header = request.headers.get('range')
    
    if range_header:
        # 解析 Range: bytes=start-end
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            
            # 确保范围有效
            if start >= file_size:
                raise HTTPException(status_code=416, detail="Range not satisfiable")
            
            end = min(end, file_size - 1)
            content_length = end - start + 1
            
            def iter_file():
                with open(file_path, 'rb') as f:
                    f.seek(start)
                    remaining = content_length
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while remaining > 0:
                        read_size = min(chunk_size, remaining)
                        data = f.read(read_size)
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            
            return StreamingResponse(
                iter_file(),
                status_code=206,
                media_type=media_type,
                headers={
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(content_length),
                }
            )
    
    # 无Range头，返回完整文件
    def iter_full_file():
        with open(file_path, 'rb') as f:
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data
    
    return StreamingResponse(
        iter_full_file(),
        media_type=media_type,
        headers={
            'Accept-Ranges': 'bytes',
            'Content-Length': str(file_size),
        }
    )


@router.get("/cover/{filename}")
async def get_cover(filename: str):
    """获取封面图片"""
    cover_path = COVER_OUTPUT_PATH / filename
    if not cover_path.exists():
        raise HTTPException(status_code=404, detail="Cover not found")
    
    return FileResponse(
        path=str(cover_path),
        media_type="image/jpeg"
    )


@router.get("/subtitle/{filename}")
async def get_subtitle(filename: str):
    """获取字幕内容"""
    subtitle_path = SUBTITLE_OUTPUT_PATH / filename
    if not subtitle_path.exists():
        raise HTTPException(status_code=404, detail="Subtitle not found")
    
    try:
        with open(subtitle_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "filename": filename,
            "content": content,
            "size": len(content.encode('utf-8'))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read subtitle: {str(e)}")


@router.get("/subtitle/download/{filename}")
async def download_subtitle(filename: str):
    """下载字幕文件"""
    subtitle_path = SUBTITLE_OUTPUT_PATH / filename
    if not subtitle_path.exists():
        raise HTTPException(status_code=404, detail="Subtitle not found")
    
    return FileResponse(
        path=str(subtitle_path),
        filename=filename,
        media_type="text/plain; charset=utf-8"
    )


@router.delete("/file/{filename}")
async def delete_file(filename: str):
    """删除下载的文件"""
    file_path = VIDEO_OUTPUT_PATH / filename
    if file_path.exists():
        os.remove(file_path)
    
    # 同时删除封面
    cover_name = Path(filename).stem + '.jpg'
    cover_path = COVER_OUTPUT_PATH / cover_name
    if cover_path.exists():
        os.remove(cover_path)
    
    return {"message": "File deleted"}


def _format_size(size: int) -> str:
    """格式化文件大小"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    else:
        return f"{size / 1024 / 1024 / 1024:.2f} GB"
