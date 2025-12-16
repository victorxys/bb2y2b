"""
提示词模板管理服务
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.prompt_template import PromptTemplate
from app.schemas.prompt_template import PromptTemplateCreate, PromptTemplateUpdate


class PromptTemplateService:
    """提示词模板管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_templates(self, skip: int = 0, limit: int = 100) -> List[PromptTemplate]:
        """获取提示词模板列表"""
        return self.db.query(PromptTemplate).offset(skip).limit(limit).all()
    
    async def get_template_by_id(self, prompt_id: str) -> Optional[PromptTemplate]:
        """根据prompt_id获取提示词模板"""
        return self.db.query(PromptTemplate).filter(PromptTemplate.prompt_id == prompt_id).first()
    
    async def create_template(self, template_data: PromptTemplateCreate) -> PromptTemplate:
        """创建新的提示词模板"""
        # 检查prompt_id是否已存在
        existing = await self.get_template_by_id(template_data.prompt_id)
        if existing:
            raise ValueError(f"Template with ID {template_data.prompt_id} already exists")
        
        db_template = PromptTemplate(**template_data.model_dump())
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template
    
    async def update_template(self, prompt_id: str, template_data: PromptTemplateUpdate) -> Optional[PromptTemplate]:
        """更新提示词模板"""
        db_template = await self.get_template_by_id(prompt_id)
        if not db_template:
            return None
        
        update_data = template_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
        
        self.db.commit()
        self.db.refresh(db_template)
        return db_template
    
    async def delete_template(self, prompt_id: str) -> bool:
        """删除提示词模板"""
        db_template = await self.get_template_by_id(prompt_id)
        if not db_template:
            return False
        
        self.db.delete(db_template)
        self.db.commit()
        return True
    
    async def get_templates_by_use_case(self, use_case: str) -> List[PromptTemplate]:
        """根据使用场景获取模板"""
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.use_case == use_case,
            PromptTemplate.is_active == True
        ).all()
    
    async def render_template(self, prompt_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """渲染提示词模板"""
        template = await self.get_template_by_id(prompt_id)
        if not template:
            return None
        
        try:
            # 简单的变量替换，可以后续升级为更复杂的模板引擎
            rendered_content = template.template_content
            for key, value in variables.items():
                rendered_content = rendered_content.replace(f"{{{key}}}", str(value))
            
            return rendered_content
        except Exception as e:
            raise ValueError(f"Template rendering failed: {str(e)}")