#!/usr/bin/env python3
"""
数据库连接测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Base

def test_database_connection():
    """测试数据库连接"""
    try:
        # 测试数据库连接
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ 数据库连接成功!")
            print(f"PostgreSQL版本: {version}")
            
        # 测试会话
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1"))
            print("✅ 数据库会话测试成功!")
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    try:
        import redis
        
        # 从配置中解析Redis URL
        redis_client = redis.from_url(settings.REDIS_URL)
        
        # 测试连接
        redis_client.ping()
        print("✅ Redis连接成功!")
        
        # 测试基本操作
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        if value == b"test_value":
            print("✅ Redis读写测试成功!")
        
        # 清理测试数据
        redis_client.delete("test_key")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 开始测试数据库和缓存连接...")
    print(f"数据库URL: {settings.DATABASE_URL}")
    print(f"Redis URL: {settings.REDIS_URL}")
    print("-" * 50)
    
    db_ok = test_database_connection()
    redis_ok = test_redis_connection()
    
    print("-" * 50)
    if db_ok and redis_ok:
        print("🎉 所有连接测试通过!")
        sys.exit(0)
    else:
        print("💥 连接测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()