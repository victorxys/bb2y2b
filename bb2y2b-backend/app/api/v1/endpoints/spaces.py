"""
UP主空间管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse
from app.services.space import SpaceService

router = APIRouter()


@router.get("/", response_model=List[SpaceResponse])
async def get_spaces(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取UP主空间列表"""
    service = SpaceService(db)
    return await service.get_spaces(skip=skip, limit=limit)


@router.post("/", response_model=SpaceResponse)
async def create_space(
    space_data: SpaceCreate,
    db: Session = Depends(get_db)
):
    """创建新的UP主空间配置"""
    service = SpaceService(db)
    return await service.create_space(space_data)


@router.get("/{space_id}", response_model=SpaceResponse)
async def get_space(
    space_id: str,
    db: Session = Depends(get_db)
):
    """获取指定UP主空间详情"""
    service = SpaceService(db)
    space = await service.get_space_by_id(space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return space


@router.put("/{space_id}", response_model=SpaceResponse)
async def update_space(
    space_id: str,
    space_data: SpaceUpdate,
    db: Session = Depends(get_db)
):
    """更新UP主空间配置"""
    service = SpaceService(db)
    space = await service.update_space(space_id, space_data)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return space


@router.delete("/{space_id}")
async def delete_space(
    space_id: str,
    db: Session = Depends(get_db)
):
    """删除UP主空间配置"""
    service = SpaceService(db)
    success = await service.delete_space(space_id)
    if not success:
        raise HTTPException(status_code=404, detail="Space not found")
    return {"message": "Space deleted successfully"}


@router.post("/{space_id}/scan")
async def scan_space(
    space_id: str,
    db: Session = Depends(get_db)
):
    """扫描UP主空间获取视频列表"""
    service = SpaceService(db)
    result = await service.scan_space(space_id)
    if not result:
        raise HTTPException(status_code=404, detail="Space not found")
    return {
        "message": "Space scan completed",
        "task_id": result.get("task_id"),
        "total_found": result.get("total_found", 0),
        "new_videos": result.get("new_videos", 0),
        "updated_videos": result.get("updated_videos", 0)
    }