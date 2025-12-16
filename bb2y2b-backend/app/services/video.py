"""
视频管理服务
"""
import time
import threading
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate
from app.services.download import download_service

# 配置日志
logger = logging.getLogger(__name__)


class VideoService:
    """视频管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_videos(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        video_type: Optional[str] = None
    ) -> List[Video]:
        """获取视频列表"""
        query = self.db.query(Video)
        
        if status:
            query = query.filter(Video.status == status)
        if video_type:
            query = query.filter(Video.video_type == video_type)
        
        return query.offset(skip).limit(limit).all()
    
    async def get_video_by_id(self, video_id: str) -> Optional[Video]:
        """根据bvid获取视频"""
        return self.db.query(Video).filter(Video.bvid == video_id).first()
    
    async def create_video(self, video_data: VideoCreate) -> Video:
        """创建新视频记录"""
        # 检查bvid是否已存在
        existing = await self.get_video_by_id(video_data.bvid)
        if existing:
            raise ValueError(f"Video with ID {video_data.bvid} already exists")
        
        db_video = Video(**video_data.model_dump())
        self.db.add(db_video)
        self.db.commit()
        self.db.refresh(db_video)
        return db_video
    
    async def update_video(self, video_id: str, video_data: VideoUpdate) -> Optional[Video]:
        """更新视频信息"""
        db_video = await self.get_video_by_id(video_id)
        if not db_video:
            return None
        
        update_data = video_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_video, field, value)
        
        self.db.commit()
        self.db.refresh(db_video)
        return db_video
    
    async def delete_video(self, video_id: str) -> bool:
        """删除视频记录"""
        db_video = await self.get_video_by_id(video_id)
        if not db_video:
            return False
        
        self.db.delete(db_video)
        self.db.commit()
        return True
    
    async def start_download(self, video_id: str) -> Optional[dict]:
        """开始下载视频（异步后台任务）"""
        from app.services.download_manager import download_manager
        
        db_video = await self.get_video_by_id(video_id)
        if not db_video:
            return None
        
        task_id = f"download_{video_id}_{int(time.time())}"
        
        # 创建下载任务
        download_manager.create_task(task_id, video_id, db_video.title)
        
        # 更新视频状态为下载中
        db_video.status = "downloading"
        self.db.commit()
        
        # 在后台线程中执行下载
        thread = threading.Thread(
            target=self._download_task,
            args=(task_id, video_id, db_video.start_p or 1, db_video.end_p, db_video.video_type or 'sleep')
        )
        thread.daemon = True
        thread.start()
        
        return {
            "task_id": task_id, 
            "status": "started",
            "message": "下载任务已启动，正在后台下载...",
            "video_url": db_video.bilibili_url
        }
    
    def _download_task(self, task_id: str, bvid: str, start_p: int, end_p: Optional[int], video_type: str):
        """后台下载任务"""
        from app.core.database import SessionLocal
        from app.services.download_manager import download_manager, TaskStatus
        
        db = SessionLocal()
        try:
            logger.info(f"开始下载任务: task_id={task_id}, bvid={bvid}")
            
            # 执行下载（带进度跟踪）
            result = download_service.download_video_with_progress(
                task_id=task_id,
                bvid=bvid,
                start_p=start_p,
                end_p=end_p,
                video_type=video_type
            )
            
            # 更新数据库
            db_video = db.query(Video).filter(Video.bvid == bvid).first()
            if db_video:
                if result:
                    db_video.status = "downloaded"
                    db_video.download_path = result.get('video_path')
                    db_video.cover_path = result.get('cover_path')
                    db_video.subtitle_path = result.get('subtitle_path')
                    logger.info(f"下载完成: {bvid}, path={result.get('video_path')}, subtitle={result.get('subtitle_path')}")
                else:
                    db_video.status = "error"
                    logger.error(f"下载失败: {bvid}")
                
                db.commit()
                
        except Exception as e:
            logger.error(f"下载任务异常: {e}")
            # 更新任务状态
            download_manager.update_task(
                task_id,
                status=TaskStatus.ERROR,
                error_message=str(e)
            )
            # 更新数据库状态
            db_video = db.query(Video).filter(Video.bvid == bvid).first()
            if db_video:
                db_video.status = "error"
                db.commit()
        finally:
            db.close()