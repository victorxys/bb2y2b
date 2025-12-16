"""初始化数据库"""
from app.core.database import engine, Base
from app.models import Space, Video, Task, AIProvider, PromptTemplate, AIAnalysisLog, SystemConfig

def init_db():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成!")

if __name__ == "__main__":
    init_db()