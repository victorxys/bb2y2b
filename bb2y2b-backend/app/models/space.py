"""
UP主空间数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Space(Base):
    """UP主空间模型"""
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(String(50), unique=True, index=True, nullable=False)
    space_name = Column(String(200), nullable=False)
    video_keyword = Column(Text, nullable=True)
    video_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_scan_time = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    videos = relationship("Video", back_populates="space", cascade="all, delete-orphan")