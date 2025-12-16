"""
视频数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Video(Base):
    """视频模型"""
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    bvid = Column(String(50), unique=True, index=True, nullable=False)  # B站BV号
    aid = Column(String(50), nullable=True)  # B站AV号
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    bilibili_url = Column(Text, nullable=True)
    cover_url = Column(Text, nullable=True)  # 原始封面URL
    video_type = Column(String(50), nullable=True)
    space_id = Column(Integer, ForeignKey("spaces.id"), nullable=True)
    status = Column(String(50), default="pending")  # pending, downloading, downloaded, uploading, uploaded
    start_p = Column(Integer, nullable=True)
    end_p = Column(Integer, nullable=True)
    duration = Column(String(20), nullable=True)  # 时长字符串如 "10:30"
    file_size = Column(BigInteger, nullable=True)
    download_path = Column(Text, nullable=True)
    cover_path = Column(Text, nullable=True)  # 本地封面路径
    subtitle_path = Column(Text, nullable=True)  # AI字幕路径
    youtube_id = Column(String(50), nullable=True)
    youtube_url = Column(Text, nullable=True)
    upload_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    space = relationship("Space", back_populates="videos")
    tasks = relationship("Task", back_populates="video", cascade="all, delete-orphan")