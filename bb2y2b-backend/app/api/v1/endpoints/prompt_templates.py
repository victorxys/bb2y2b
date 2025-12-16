"""
提示词模板管理API端点
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse
from app.services.prompt_template import PromptTemplateService

router = APIRouter()


@router.get("/", response_model=List[PromptTemplateResponse])
async def get_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取提示词模板列表"""
    service = PromptTemplateService(db)
    return await service.get_templates(skip=skip, limit=limit)


@router.post("/", response_model=PromptTemplateResponse)
async def create_template(
    template_data: PromptTemplateCreate,
    db: Session = Depends(get_db)
):
    """创建新的提示词模板"""
    service = PromptTemplateService(db)
    try:
        return await service.create_template(template_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{prompt_id}", response_model=PromptTemplateResponse)
async def get_template(
    prompt_id: str,
    db: Session = Depends(get_db)
):
    """获取指定提示词模板详情"""
    service = PromptTemplateService(db)
    template = await service.get_template_by_id(prompt_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{prompt_id}", response_model=PromptTemplateResponse)
async def update_template(
    prompt_id: str,
    template_data: PromptTemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新提示词模板"""
    service = PromptTemplateService(db)
    template = await service.update_template(prompt_id, template_data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{prompt_id}")
async def delete_template(
    prompt_id: str,
    db: Session = Depends(get_db)
):
    """删除提示词模板"""
    service = PromptTemplateService(db)
    success = await service.delete_template(prompt_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}


@router.get("/use-case/{use_case}", response_model=List[PromptTemplateResponse])
async def get_templates_by_use_case(
    use_case: str,
    db: Session = Depends(get_db)
):
    """根据使用场景获取模板"""
    service = PromptTemplateService(db)
    return await service.get_templates_by_use_case(use_case)


@router.post("/{prompt_id}/render")
async def render_template(
    prompt_id: str,
    variables: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """渲染提示词模板"""
    service = PromptTemplateService(db)
    try:
        rendered_content = await service.render_template(prompt_id, variables)
        if rendered_content is None:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"rendered_content": rendered_content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))