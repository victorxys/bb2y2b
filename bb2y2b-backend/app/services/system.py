"""
系统状态和配置服务
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.video import Video
from app.models.task import Task
from app.models.space import Space
from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class SystemService:
    """系统服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统运行状态"""
        # 获取各种统计信息
        total_spaces = self.db.query(func.count(Space.id)).scalar()
        active_spaces = self.db.query(func.count(Space.id)).filter(Space.is_active == True).scalar()
        
        total_videos = self.db.query(func.count(Video.id)).scalar()
        pending_videos = self.db.query(func.count(Video.id)).filter(Video.status == "pending").scalar()
        downloading_videos = self.db.query(func.count(Video.id)).filter(Video.status == "downloading").scalar()
        completed_videos = self.db.query(func.count(Video.id)).filter(Video.status == "completed").scalar()
        
        running_tasks = self.db.query(func.count(Task.id)).filter(Task.status == "running").scalar()
        pending_tasks = self.db.query(func.count(Task.id)).filter(Task.status == "pending").scalar()
        
        return {
            "status": "running",
            "spaces": {
                "total": total_spaces,
                "active": active_spaces
            },
            "videos": {
                "total": total_videos,
                "pending": pending_videos,
                "downloading": downloading_videos,
                "completed": completed_videos
            },
            "tasks": {
                "running": running_tasks,
                "pending": pending_tasks
            },
            "timestamp": func.now()
        }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        # 获取更详细的统计信息
        video_stats_by_type = self.db.query(
            Video.video_type, 
            func.count(Video.id)
        ).group_by(Video.video_type).all()
        
        task_stats_by_type = self.db.query(
            Task.task_type,
            func.count(Task.id)
        ).group_by(Task.task_type).all()
        
        return {
            "video_stats_by_type": dict(video_stats_by_type),
            "task_stats_by_type": dict(task_stats_by_type),
            "timestamp": func.now()
        }
    
    # System Config Management Methods
    async def get_configs(self, skip: int = 0, limit: int = 100) -> List[SystemConfig]:
        """获取系统配置列表"""
        return self.db.query(SystemConfig).offset(skip).limit(limit).all()
    
    async def get_config_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """根据配置键获取配置"""
        return self.db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    
    async def create_config(self, config_data: SystemConfigCreate) -> SystemConfig:
        """创建新的系统配置"""
        # 检查config_key是否已存在
        existing = await self.get_config_by_key(config_data.config_key)
        if existing:
            raise ValueError(f"Config with key {config_data.config_key} already exists")
        
        db_config = SystemConfig(**config_data.model_dump())
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        return db_config
    
    async def update_config(self, config_key: str, config_data: SystemConfigUpdate) -> Optional[SystemConfig]:
        """更新系统配置"""
        db_config = await self.get_config_by_key(config_key)
        if not db_config:
            return None
        
        update_data = config_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_config, field, value)
        
        self.db.commit()
        self.db.refresh(db_config)
        return db_config
    
    async def delete_config(self, config_key: str) -> bool:
        """删除系统配置"""
        db_config = await self.get_config_by_key(config_key)
        if not db_config:
            return False
        
        self.db.delete(db_config)
        self.db.commit()
        return True
    
    async def get_config_value(self, config_key: str, default_value: str = None) -> Optional[str]:
        """获取配置值"""
        config = await self.get_config_by_key(config_key)
        return config.config_value if config else default_value
    
    async def set_config_value(self, config_key: str, config_value: str, description: str = None) -> SystemConfig:
        """设置配置值（如果不存在则创建）"""
        existing = await self.get_config_by_key(config_key)
        
        if existing:
            # 更新现有配置
            update_data = SystemConfigUpdate(config_value=config_value)
            if description:
                update_data.description = description
            return await self.update_config(config_key, update_data)
        else:
            # 创建新配置
            create_data = SystemConfigCreate(
                config_key=config_key,
                config_value=config_value,
                description=description
            )
            return await self.create_config(create_data)