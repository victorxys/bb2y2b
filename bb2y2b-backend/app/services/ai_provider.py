"""
AI Provider管理服务
"""
import base64
from typing import List, Optional
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

from app.models.ai_provider import AIProvider
from app.schemas.ai_provider import AIProviderCreate, AIProviderUpdate


class AIProviderService:
    """AI Provider管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        # TODO: 从环境变量或配置中获取加密密钥
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """加密API密钥"""
        return base64.b64encode(self.cipher.encrypt(api_key.encode())).decode()
    
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """解密API密钥"""
        return self.cipher.decrypt(base64.b64decode(encrypted_key.encode())).decode()
    
    async def get_providers(self, skip: int = 0, limit: int = 100) -> List[AIProvider]:
        """获取AI Provider列表"""
        return self.db.query(AIProvider).offset(skip).limit(limit).all()
    
    async def get_provider_by_id(self, provider_id: str) -> Optional[AIProvider]:
        """根据provider_id获取AI Provider"""
        return self.db.query(AIProvider).filter(AIProvider.provider_id == provider_id).first()
    
    async def create_provider(self, provider_data: AIProviderCreate) -> AIProvider:
        """创建新的AI Provider"""
        # 检查provider_id是否已存在
        existing = await self.get_provider_by_id(provider_data.provider_id)
        if existing:
            raise ValueError(f"Provider with ID {provider_data.provider_id} already exists")
        
        # 加密API密钥
        encrypted_key = self._encrypt_api_key(provider_data.api_key)
        
        # 创建数据库记录
        provider_dict = provider_data.model_dump(exclude={'api_key'})
        provider_dict['api_key_encrypted'] = encrypted_key
        
        db_provider = AIProvider(**provider_dict)
        self.db.add(db_provider)
        self.db.commit()
        self.db.refresh(db_provider)
        return db_provider
    
    async def update_provider(self, provider_id: str, provider_data: AIProviderUpdate) -> Optional[AIProvider]:
        """更新AI Provider配置"""
        db_provider = await self.get_provider_by_id(provider_id)
        if not db_provider:
            return None
        
        update_data = provider_data.model_dump(exclude_unset=True)
        
        # 如果更新API密钥，需要重新加密
        if 'api_key' in update_data:
            update_data['api_key_encrypted'] = self._encrypt_api_key(update_data.pop('api_key'))
        
        for field, value in update_data.items():
            setattr(db_provider, field, value)
        
        self.db.commit()
        self.db.refresh(db_provider)
        return db_provider
    
    async def delete_provider(self, provider_id: str) -> bool:
        """删除AI Provider"""
        db_provider = await self.get_provider_by_id(provider_id)
        if not db_provider:
            return False
        
        self.db.delete(db_provider)
        self.db.commit()
        return True
    
    async def get_active_providers(self) -> List[AIProvider]:
        """获取所有活跃的AI Provider"""
        return self.db.query(AIProvider).filter(AIProvider.is_active == True).all()
    
    async def increment_usage(self, provider_id: str, tokens_used: int) -> bool:
        """增加Provider使用量"""
        db_provider = await self.get_provider_by_id(provider_id)
        if not db_provider:
            return False
        
        db_provider.current_usage += tokens_used
        self.db.commit()
        return True