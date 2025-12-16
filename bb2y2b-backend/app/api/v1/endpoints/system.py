"""
系统管理API端点
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse
from app.services.system import SystemService

router = APIRouter()


@router.get("/status")
async def get_system_status(db: Session = Depends(get_db)):
    """获取系统运行状态"""
    service = SystemService(db)
    return await service.get_system_status()


@router.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """获取系统统计信息"""
    service = SystemService(db)
    return await service.get_system_stats()


@router.get("/configs", response_model=List[SystemConfigResponse])
async def get_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取系统配置列表"""
    service = SystemService(db)
    return await service.get_configs(skip=skip, limit=limit)


@router.post("/configs", response_model=SystemConfigResponse)
async def create_config(
    config_data: SystemConfigCreate,
    db: Session = Depends(get_db)
):
    """创建新的系统配置"""
    service = SystemService(db)
    try:
        return await service.create_config(config_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/configs/{config_key}", response_model=SystemConfigResponse)
async def get_config(
    config_key: str,
    db: Session = Depends(get_db)
):
    """获取指定系统配置"""
    service = SystemService(db)
    config = await service.get_config_by_key(config_key)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.put("/configs/{config_key}", response_model=SystemConfigResponse)
async def update_config(
    config_key: str,
    config_data: SystemConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    service = SystemService(db)
    config = await service.update_config(config_key, config_data)
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    return config


@router.delete("/configs/{config_key}")
async def delete_config(
    config_key: str,
    db: Session = Depends(get_db)
):
    """删除系统配置"""
    service = SystemService(db)
    success = await service.delete_config(config_key)
    if not success:
        raise HTTPException(status_code=404, detail="Config not found")
    return {"message": "Config deleted successfully"}


@router.get("/configs/{config_key}/value")
async def get_config_value(
    config_key: str,
    default_value: str = None,
    db: Session = Depends(get_db)
):
    """获取配置值"""
    service = SystemService(db)
    value = await service.get_config_value(config_key, default_value)
    return {"config_key": config_key, "config_value": value}


@router.post("/configs/{config_key}/value")
async def set_config_value(
    config_key: str,
    config_value: str,
    description: str = None,
    db: Session = Depends(get_db)
):
    """设置配置值"""
    service = SystemService(db)
    config = await service.set_config_value(config_key, config_value, description)
    return config