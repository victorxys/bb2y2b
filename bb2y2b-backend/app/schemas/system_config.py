"""
系统配置Pydantic模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SystemConfigBase(BaseModel):
    """系统配置基础模式"""
    config_key: str = Field(..., description="配置键")
    config_value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, description="配置描述")


class SystemConfigCreate(SystemConfigBase):
    """创建系统配置模式"""
    pass


class SystemConfigUpdate(BaseModel):
    """更新系统配置模式"""
    config_value: Optional[str] = None
    description: Optional[str] = None


class SystemConfigResponse(SystemConfigBase):
    """系统配置响应模式"""
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True