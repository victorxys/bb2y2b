"""
视频Pydantic模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class VideoBase(BaseModel):
    """视频基础模式"""
    bvid: str = Field(..., description="B站BV号")
    title: str = Field(..., description="视频标题")
    bilibili_url: Optional[str] = Field(None, description="B站视频URL")
    video_type: Optional[str] = Field(None, description="视频类型")
    start_p: Optional[int] = Field(None, description="开始分集")
    end_p: Optional[int] = Field(None, description="结束分集")


class VideoCreate(VideoBase):
    """创建视频模式"""
    aid: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    space_id: Optional[int] = None


class VideoUpdate(BaseModel):
    """更新视频模式"""
    title: Optional[str] = None
    video_type: Optional[str] = None
    start_p: Optional[int] = None
    end_p: Optional[int] = None
    status: Optional[str] = None


class VideoResponse(BaseModel):
    """视频响应模式"""
    id: int
    bvid: str
    aid: Optional[str] = None
    title: str
    description: Optional[str] = None
    bilibili_url: Optional[str] = None
    cover_url: Optional[str] = None
    video_type: Optional[str] = None
    space_id: Optional[int] = None
    status: str
    start_p: Optional[int] = None
    end_p: Optional[int] = None
    duration: Optional[str] = None
    file_size: Optional[int] = None
    download_path: Optional[str] = None
    cover_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    youtube_id: Optional[str] = None
    youtube_url: Optional[str] = None
    upload_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True