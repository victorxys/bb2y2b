"""
AI分析日志数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AIAnalysisLog(Base):
    """AI分析日志模型"""
    __tablename__ = "ai_analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("ai_providers.id"), nullable=True)
    prompt_id = Column(Integer, ForeignKey("prompt_templates.id"), nullable=True)
    input_content = Column(Text, nullable=False)
    output_content = Column(Text, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    analysis_type = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Integer, nullable=True)  # in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video")
    provider = relationship("AIProvider")
    prompt_template = relationship("PromptTemplate")