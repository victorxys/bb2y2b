"""
AI Provider数据模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.sql import func

from app.core.database import Base


class AIProvider(Base):
    """AI Provider模型"""
    __tablename__ = "ai_providers"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String(50), unique=True, index=True, nullable=False)
    provider_name = Column(String(100), nullable=False)
    provider_type = Column(String(50), nullable=False)  # gemini, openai, claude
    api_key_encrypted = Column(Text, nullable=False)
    api_endpoint = Column(Text, nullable=True)
    model_name = Column(String(100), nullable=False)
    max_tokens = Column(Integer, default=4000)
    temperature = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    usage_quota = Column(Integer, nullable=True)
    current_usage = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())