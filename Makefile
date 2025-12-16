# BB2Y2B Makefile

.PHONY: help install dev backend frontend clean test

help: ## 显示帮助信息
	@echo "BB2Y2B - B站视频下载管理系统"
	@echo ""
	@echo "可用命令:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## 安装所有依赖
	@echo "📦 安装后端依赖..."
	cd bb2y2b-backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "📦 安装前端依赖..."
	cd bb2y2b-vite-frontend && npm install
	@echo "✅ 依赖安装完成"

dev: ## 启动开发环境
	@./start-dev.sh

backend: ## 仅启动后端服务
	@echo "📡 启动后端服务..."
	cd bb2y2b-backend && source venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend: ## 仅启动前端服务
	@echo "🎨 启动前端服务..."
	cd bb2y2b-vite-frontend && npm run dev

init-db: ## 初始化数据库
	@echo "🗄️ 初始化数据库..."
	cd bb2y2b-backend && source venv/bin/activate && python init_db.py

clean: ## 清理临时文件
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	rm -rf bb2y2b-backend/venv 2>/dev/null || true
	rm -rf bb2y2b-vite-frontend/node_modules 2>/dev/null || true
	rm -rf bb2y2b-vite-frontend/dist 2>/dev/null || true
	@echo "✅ 清理完成"

build: ## 构建生产版本
	@echo "🏗️ 构建前端..."
	cd bb2y2b-vite-frontend && npm run build
	@echo "✅ 构建完成"

test: ## 运行测试
	@echo "🧪 运行测试..."
	cd bb2y2b-backend && source venv/bin/activate && python -m pytest
	cd bb2y2b-vite-frontend && npm run test

lint: ## 代码检查
	@echo "🔍 检查后端代码..."
	cd bb2y2b-backend && source venv/bin/activate && flake8 app/
	@echo "🔍 检查前端代码..."
	cd bb2y2b-vite-frontend && npm run lint