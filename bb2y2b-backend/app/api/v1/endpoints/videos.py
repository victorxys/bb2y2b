"""
视频管理API端点
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.video import VideoCreate, VideoUpdate, VideoResponse
from app.services.video import VideoService

router = APIRouter()


@router.get("/", response_model=List[VideoResponse])
async def get_videos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status"),
    video_type: Optional[str] = Query(None, description="Filter by video type"),
    db: Session = Depends(get_db)
):
    """获取视频列表"""
    service = VideoService(db)
    return await service.get_videos(
        skip=skip, 
        limit=limit, 
        status=status, 
        video_type=video_type
    )


@router.post("/", response_model=VideoResponse)
async def create_video(
    video_data: VideoCreate,
    db: Session = Depends(get_db)
):
    """手动添加视频到下载列表"""
    service = VideoService(db)
    return await service.create_video(video_data)


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: Session = Depends(get_db)
):
    """获取指定视频详情"""
    service = VideoService(db)
    video = await service.get_video_by_id(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: str,
    video_data: VideoUpdate,
    db: Session = Depends(get_db)
):
    """更新视频信息"""
    service = VideoService(db)
    video = await service.update_video(video_id, video_data)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db)
):
    """删除视频记录"""
    service = VideoService(db)
    success = await service.delete_video(video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Video deleted successfully"}


@router.post("/{video_id}/download")
async def start_download(
    video_id: str,
    db: Session = Depends(get_db)
):
    """开始下载指定视频"""
    service = VideoService(db)
    result = await service.start_download(video_id)
    if not result:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Download started", "task_id": result.get("task_id")}