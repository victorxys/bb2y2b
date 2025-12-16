"""
任务管理服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskService:
    """任务管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_tasks(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[Task]:
        """获取任务列表"""
        query = self.db.query(Task)
        
        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        return query.offset(skip).limit(limit).all()
    
    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """根据task_id获取任务"""
        return self.db.query(Task).filter(Task.task_id == task_id).first()
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        db_task = await self.get_task_by_id(task_id)
        if not db_task or db_task.status in ["completed", "failed", "cancelled"]:
            return False
        
        db_task.status = "cancelled"
        self.db.commit()
        return True
    
    async def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        db_task = await self.get_task_by_id(task_id)
        if not db_task:
            return None
        
        return {
            "task_id": db_task.task_id,
            "status": db_task.status,
            "progress": db_task.progress,
            "error_message": db_task.error_message,
            "created_at": db_task.created_at,
            "completed_at": db_task.completed_at
        }