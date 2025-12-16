"""
提示词模板数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON

from app.core.database import Base


class PromptTemplate(Base):
    """提示词模板模型"""
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(String(50), unique=True, index=True, nullable=False)
    template_name = Column(String(200), nullable=False)
    template_content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)
    use_case = Column(String(100), nullable=False)
    provider_type = Column(String(50), nullable=True)
    version = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())