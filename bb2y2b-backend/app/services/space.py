"""
UP主空间管理服务
"""
import time
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.space import Space
from app.models.video import Video
from app.schemas.space import SpaceCreate, SpaceUpdate
from app.services.bilibili import bilibili_service


class SpaceService:
    """UP主空间管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_spaces(self, skip: int = 0, limit: int = 100) -> List[Space]:
        """获取空间列表"""
        return self.db.query(Space).offset(skip).limit(limit).all()
    
    async def get_space_by_id(self, space_id: str) -> Optional[Space]:
        """根据space_id获取空间"""
        return self.db.query(Space).filter(Space.space_id == space_id).first()
    
    async def create_space(self, space_data: SpaceCreate) -> Space:
        """创建新空间"""
        existing = await self.get_space_by_id(space_data.space_id)
        if existing:
            raise ValueError(f"Space with ID {space_data.space_id} already exists")
        
        db_space = Space(**space_data.model_dump())
        self.db.add(db_space)
        self.db.commit()
        self.db.refresh(db_space)
        return db_space
    
    async def update_space(self, space_id: str, space_data: SpaceUpdate) -> Optional[Space]:
        """更新空间配置"""
        db_space = await self.get_space_by_id(space_id)
        if not db_space:
            return None
        
        update_data = space_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_space, field, value)
        
        self.db.commit()
        self.db.refresh(db_space)
        return db_space
    
    async def delete_space(self, space_id: str) -> bool:
        """删除空间配置"""
        db_space = await self.get_space_by_id(space_id)
        if not db_space:
            return False
        
        self.db.delete(db_space)
        self.db.commit()
        return True
    
    async def scan_space(self, space_id: str) -> Optional[dict]:
        """扫描空间获取视频列表并保存到数据库"""
        db_space = await self.get_space_by_id(space_id)
        if not db_space:
            return None
        
        # 调用B站API获取视频列表
        videos = bilibili_service.scan_all_videos(
            space_id=space_id,
            video_keyword=db_space.video_keyword
        )
        
        # 保存视频到数据库
        new_count = 0
        updated_count = 0
        
        for video_data in videos:
            bvid = video_data.get('bvid', '')
            if not bvid:
                continue
            
            # 检查视频是否已存在
            existing_video = self.db.query(Video).filter(Video.bvid == bvid).first()
            
            if existing_video:
                # 更新现有视频
                existing_video.title = video_data.get('title', '')
                existing_video.description = video_data.get('description', '')
                existing_video.cover_url = video_data.get('pic', '')
                existing_video.duration = video_data.get('length', '')
                updated_count += 1
            else:
                # 创建新视频
                new_video = Video(
                    bvid=bvid,
                    aid=str(video_data.get('aid', '')),
                    title=video_data.get('title', ''),
                    description=video_data.get('description', ''),
                    cover_url=video_data.get('pic', ''),
                    duration=video_data.get('length', ''),
                    space_id=db_space.id,
                    video_type=db_space.video_type,
                    bilibili_url=f"https://www.bilibili.com/video/{bvid}",
                    status='pending',
                    created_at=datetime.utcnow()
                )
                self.db.add(new_video)
                new_count += 1
        
        # 更新空间的最后扫描时间
        db_space.last_scan_time = datetime.utcnow()
        self.db.commit()
        
        return {
            "task_id": f"scan_{space_id}_{int(time.time())}",
            "status": "completed",
            "total_found": len(videos),
            "new_videos": new_count,
            "updated_videos": updated_count
        }