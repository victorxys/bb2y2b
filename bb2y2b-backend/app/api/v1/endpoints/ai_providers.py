"""
AI Provider管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ai_provider import AIProviderCreate, AIProviderUpdate, AIProviderResponse
from app.services.ai_provider import AIProviderService

router = APIRouter()


@router.get("/", response_model=List[AIProviderResponse])
async def get_providers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取AI Provider列表"""
    service = AIProviderService(db)
    return await service.get_providers(skip=skip, limit=limit)


@router.post("/", response_model=AIProviderResponse)
async def create_provider(
    provider_data: AIProviderCreate,
    db: Session = Depends(get_db)
):
    """创建新的AI Provider"""
    service = AIProviderService(db)
    try:
        return await service.create_provider(provider_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{provider_id}", response_model=AIProviderResponse)
async def get_provider(
    provider_id: str,
    db: Session = Depends(get_db)
):
    """获取指定AI Provider详情"""
    service = AIProviderService(db)
    provider = await service.get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.put("/{provider_id}", response_model=AIProviderResponse)
async def update_provider(
    provider_id: str,
    provider_data: AIProviderUpdate,
    db: Session = Depends(get_db)
):
    """更新AI Provider配置"""
    service = AIProviderService(db)
    provider = await service.update_provider(provider_id, provider_data)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: str,
    db: Session = Depends(get_db)
):
    """删除AI Provider"""
    service = AIProviderService(db)
    success = await service.delete_provider(provider_id)
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted successfully"}


@router.get("/active/list", response_model=List[AIProviderResponse])
async def get_active_providers(db: Session = Depends(get_db)):
    """获取所有活跃的AI Provider"""
    service = AIProviderService(db)
    return await service.get_active_providers()


@router.post("/{provider_id}/usage")
async def increment_usage(
    provider_id: str,
    tokens_used: int,
    db: Session = Depends(get_db)
):
    """增加Provider使用量"""
    service = AIProviderService(db)
    success = await service.increment_usage(provider_id, tokens_used)
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Usage updated successfully"}