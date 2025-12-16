# BB2Y2B Backend API

BB2Y2B现代化升级项目的后端API服务，基于FastAPI构建。

## 功能特性

- 🚀 FastAPI + SQLAlchemy + PostgreSQL
- 📊 UP主空间管理和视频扫描
- 🎬 视频下载和处理管道
- 🤖 AI内容分析和优化
- 📤 YouTube自动上传
- 🔄 Celery异步任务队列
- 📈 实时状态监控

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 13+
- Redis 6+

### 安装依赖

```bash
# 使用Poetry安装依赖
poetry install

# 或使用pip
pip install -r requirements.txt
```

### 环境配置

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

### 数据库迁移

```bash
# 初始化数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 启动服务

```bash
# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用Poetry
poetry run uvicorn app.main:app --reload
```

### 启动Celery Worker

```bash
# 启动Celery worker
celery -A app.tasks.celery worker --loglevel=info

# 启动Celery beat (定时任务)
celery -A app.tasks.celery beat --loglevel=info
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
bb2y2b-backend/
├── app/
│   ├── api/                # API路由
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── schemas/            # Pydantic模式
│   ├── services/           # 业务逻辑
│   └── tasks/              # Celery任务
├── alembic/                # 数据库迁移
├── tests/                  # 测试文件
└── pyproject.toml          # 项目配置
```

## 开发指南

### 代码格式化

```bash
# 格式化代码
black app/
isort app/

# 类型检查
mypy app/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t bb2y2b-backend .

# 运行容器
docker run -p 8000:8000 bb2y2b-backend
```

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d
```

## 许可证

MIT License