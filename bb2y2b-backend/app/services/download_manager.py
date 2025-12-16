"""
下载任务管理器 - 管理下载任务状态和进度
"""
import time
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    MERGING = "merging"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class DownloadProgress:
    """下载进度信息"""
    task_id: str
    bvid: str
    title: str = ""
    status: TaskStatus = TaskStatus.PENDING
    
    # 进度信息
    current_page: int = 0
    total_pages: int = 0
    current_bytes: int = 0
    total_bytes: int = 0
    
    # 速度和时间
    speed: float = 0.0  # bytes/s
    eta: int = 0  # 预估剩余秒数
    
    # 阶段信息
    stage: str = "waiting"  # waiting, fetching_info, fetching_links, downloading, merging, downloading_cover, completed
    stage_message: str = ""
    
    # 合并进度
    merge_progress: float = 0.0  # 0-100
    total_duration: float = 0.0  # 总时长（秒）
    
    # 时间戳
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 结果
    download_path: Optional[str] = None
    cover_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    error_message: Optional[str] = None
    
    # 速度计算用
    _last_bytes: int = field(default=0, repr=False)
    _last_time: float = field(default=0.0, repr=False)
    _speed_samples: List[float] = field(default_factory=list, repr=False)
    
    def update_speed(self):
        """更新下载速度"""
        current_time = time.time()
        if self._last_time > 0:
            time_diff = current_time - self._last_time
            if time_diff > 0:
                bytes_diff = self.current_bytes - self._last_bytes
                instant_speed = bytes_diff / time_diff
                
                # 使用滑动平均计算速度
                self._speed_samples.append(instant_speed)
                if len(self._speed_samples) > 10:
                    self._speed_samples.pop(0)
                
                self.speed = sum(self._speed_samples) / len(self._speed_samples)
                
                # 计算预估时间
                if self.speed > 0 and self.total_bytes > 0:
                    remaining_bytes = self.total_bytes - self.current_bytes
                    self.eta = int(remaining_bytes / self.speed)
        
        self._last_bytes = self.current_bytes
        self._last_time = current_time
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "bvid": self.bvid,
            "title": self.title,
            "status": self.status.value,
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "current_bytes": self.current_bytes,
            "total_bytes": self.total_bytes,
            "speed": self.speed,
            "speed_formatted": self._format_speed(self.speed),
            "eta": self.eta,
            "eta_formatted": self._format_eta(self.eta),
            "progress_percent": self._calc_progress(),
            "stage": self.stage,
            "stage_message": self.stage_message,
            "merge_progress": self.merge_progress,
            "total_duration": self.total_duration,
            "total_duration_formatted": self._format_duration(self.total_duration),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "download_path": self.download_path,
            "cover_path": self.cover_path,
            "subtitle_path": self.subtitle_path,
            "error_message": self.error_message,
        }
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """格式化时长"""
        seconds = int(seconds)
        if seconds <= 0:
            return "--"
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            return f"{seconds // 60}分{seconds % 60}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分"
    
    def _calc_progress(self) -> float:
        """计算总进度百分比"""
        if self.status == TaskStatus.COMPLETED:
            return 100.0
        if self.total_pages == 0:
            return 0.0
        
        # 基于分P进度
        page_progress = (self.current_page / self.total_pages) * 100
        
        # 如果有字节进度，更精确计算
        if self.total_bytes > 0 and self.current_bytes > 0:
            byte_progress = (self.current_bytes / self.total_bytes) * 100
            # 当前分P的进度
            current_page_progress = byte_progress / self.total_pages
            return min(99.9, ((self.current_page - 1) / self.total_pages * 100) + current_page_progress)
        
        return min(99.9, page_progress)
    
    @staticmethod
    def _format_speed(speed: float) -> str:
        """格式化速度"""
        if speed < 1024:
            return f"{speed:.0f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed / 1024 / 1024:.2f} MB/s"
    
    @staticmethod
    def _format_eta(seconds: int) -> str:
        """格式化预估时间"""
        if seconds <= 0:
            return "--"
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            return f"{seconds // 60}分{seconds % 60}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分"


class DownloadManager:
    """下载任务管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._tasks: Dict[str, DownloadProgress] = {}
        self._task_lock = threading.Lock()
    
    def create_task(self, task_id: str, bvid: str, title: str = "") -> DownloadProgress:
        """创建下载任务"""
        with self._task_lock:
            task = DownloadProgress(
                task_id=task_id,
                bvid=bvid,
                title=title,
                status=TaskStatus.PENDING,
                started_at=datetime.now()
            )
            self._tasks[task_id] = task
            logger.info(f"创建下载任务: {task_id}, bvid={bvid}")
            return task
    
    def get_task(self, task_id: str) -> Optional[DownloadProgress]:
        """获取任务"""
        return self._tasks.get(task_id)
    
    def get_task_by_bvid(self, bvid: str) -> Optional[DownloadProgress]:
        """根据bvid获取最新任务"""
        with self._task_lock:
            for task in reversed(list(self._tasks.values())):
                if task.bvid == bvid:
                    return task
        return None
    
    def get_all_tasks(self) -> List[Dict]:
        """获取所有任务"""
        with self._task_lock:
            return [task.to_dict() for task in self._tasks.values()]
    
    def get_active_tasks(self) -> List[Dict]:
        """获取活跃任务（下载中/合并中）"""
        with self._task_lock:
            active = [
                task.to_dict() for task in self._tasks.values()
                if task.status in [TaskStatus.DOWNLOADING, TaskStatus.MERGING, TaskStatus.PENDING]
            ]
            return active
    
    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        current_page: Optional[int] = None,
        total_pages: Optional[int] = None,
        current_bytes: Optional[int] = None,
        total_bytes: Optional[int] = None,
        stage: Optional[str] = None,
        stage_message: Optional[str] = None,
        download_path: Optional[str] = None,
        cover_path: Optional[str] = None,
        subtitle_path: Optional[str] = None,
        error_message: Optional[str] = None,
        title: Optional[str] = None,
        merge_progress: Optional[float] = None,
        total_duration: Optional[float] = None,
    ):
        """更新任务状态"""
        task = self._tasks.get(task_id)
        if not task:
            return
        
        with self._task_lock:
            if status is not None:
                task.status = status
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now()
            if current_page is not None:
                task.current_page = current_page
            if total_pages is not None:
                task.total_pages = total_pages
            if current_bytes is not None:
                task.current_bytes = current_bytes
                task.update_speed()
            if total_bytes is not None:
                task.total_bytes = total_bytes
            if stage is not None:
                task.stage = stage
            if stage_message is not None:
                task.stage_message = stage_message
            if download_path is not None:
                task.download_path = download_path
            if cover_path is not None:
                task.cover_path = cover_path
            if subtitle_path is not None:
                task.subtitle_path = subtitle_path
            if error_message is not None:
                task.error_message = error_message
            if title is not None:
                task.title = title
            if merge_progress is not None:
                task.merge_progress = merge_progress
            if total_duration is not None:
                task.total_duration = total_duration
    
    def remove_task(self, task_id: str):
        """移除任务"""
        with self._task_lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
    
    def clear_completed(self):
        """清除已完成的任务"""
        with self._task_lock:
            to_remove = [
                tid for tid, task in self._tasks.items()
                if task.status in [TaskStatus.COMPLETED, TaskStatus.ERROR, TaskStatus.CANCELLED]
            ]
            for tid in to_remove:
                del self._tasks[tid]


# 单例实例
download_manager = DownloadManager()
