"""
任务Pydantic模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """任务基础模式"""
    task_id: str = Field(..., description="任务ID")
    task_type: str = Field(..., description="任务类型")
    video_id: Optional[int] = Field(None, description="关联视频ID")


class TaskResponse(TaskBase):
    """任务响应模式"""
    id: int
    status: str
    progress: float
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True