"""
AI Provider Pydantic模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AIProviderBase(BaseModel):
    """AI Provider基础模式"""
    provider_id: str = Field(..., description="Provider唯一标识")
    provider_name: str = Field(..., description="Provider名称")
    provider_type: str = Field(..., description="Provider类型 (gemini, openai, claude)")
    api_endpoint: Optional[str] = Field(None, description="API端点URL")
    model_name: str = Field(..., description="模型名称")
    max_tokens: int = Field(4000, description="最大token数")
    temperature: float = Field(0.7, description="温度参数")
    is_active: bool = Field(True, description="是否启用")
    usage_quota: Optional[int] = Field(None, description="使用配额")


class AIProviderCreate(AIProviderBase):
    """创建AI Provider模式"""
    api_key: str = Field(..., description="API密钥")


class AIProviderUpdate(BaseModel):
    """更新AI Provider模式"""
    provider_name: Optional[str] = None
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    is_active: Optional[bool] = None
    usage_quota: Optional[int] = None


class AIProviderResponse(AIProviderBase):
    """AI Provider响应模式"""
    id: int
    current_usage: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True