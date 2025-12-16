"""
提示词模板Pydantic模式
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PromptTemplateBase(BaseModel):
    """提示词模板基础模式"""
    prompt_id: str = Field(..., description="提示词模板唯一标识")
    template_name: str = Field(..., description="模板名称")
    template_content: str = Field(..., description="模板内容")
    variables: Optional[Dict[str, Any]] = Field(None, description="模板变量定义")
    use_case: str = Field(..., description="使用场景")
    provider_type: Optional[str] = Field(None, description="适用的Provider类型")
    version: Optional[str] = Field("1.0", description="模板版本")
    is_active: bool = Field(True, description="是否启用")


class PromptTemplateCreate(PromptTemplateBase):
    """创建提示词模板模式"""
    pass


class PromptTemplateUpdate(BaseModel):
    """更新提示词模板模式"""
    template_name: Optional[str] = None
    template_content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    use_case: Optional[str] = None
    provider_type: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None


class PromptTemplateResponse(PromptTemplateBase):
    """提示词模板响应模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
