"""
UP主空间Pydantic模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SpaceBase(BaseModel):
    """空间基础模式"""
    space_id: str = Field(..., description="B站UP主空间ID")
    space_name: str = Field(..., description="UP主空间名称")
    video_keyword: Optional[str] = Field(None, description="视频关键字过滤器")
    video_type: str = Field(..., description="视频类型")
    is_active: bool = Field(True, description="是否启用")


class SpaceCreate(SpaceBase):
    """创建空间模式"""
    pass


class SpaceUpdate(BaseModel):
    """更新空间模式"""
    space_name: Optional[str] = None
    video_keyword: Optional[str] = None
    video_type: Optional[str] = None
    is_active: Optional[bool] = None


class SpaceResponse(SpaceBase):
    """空间响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_scan_time: Optional[datetime] = None

    class Config:
        from_attributes = True