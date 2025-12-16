# BB2Y2B - B站视频下载管理系统

一个现代化的B站视频下载和管理系统，支持UP主空间扫描、视频下载、AI字幕获取等功能。

## 功能特性

- 🎯 **UP主空间管理**: 添加和管理UP主空间，自动扫描最新视频
- 📥 **智能下载**: 支持音频/视频下载，自动合并多分P内容
- 🤖 **AI字幕**: 自动获取B站AI生成的视频总结和大纲
- 📊 **进度跟踪**: 实时显示下载进度、速度和预估时间
- 🎵 **在线播放**: 支持在线预览和播放已下载的音频/视频
- 📱 **现代界面**: 基于React + TypeScript的响应式Web界面

## 技术栈

### 后端
- **FastAPI**: 现代Python Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **MoviePy**: 音视频处理
- **Requests**: HTTP请求处理

### 前端
- **Vite + React 18**: 现代前端构建工具和框架
- **TypeScript**: 类型安全的JavaScript
- **Tailwind CSS**: 实用优先的CSS框架
- **React Query**: 数据获取和状态管理
- **Lucide React**: 现代图标库

## 项目结构

```
bb2y2b/
├── bb2y2b-backend/          # FastAPI后端
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic模式
│   │   └── services/        # 业务逻辑
│   ├── alembic/             # 数据库迁移
│   └── requirements.txt     # Python依赖
├── bb2y2b-vite-frontend/    # Vite + React前端
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── hooks/           # 自定义Hooks
│   │   └── lib/             # 工具库和API
│   └── package.json         # Node.js依赖
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端设置

1. 进入后端目录：
```bash
cd bb2y2b-backend
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

5. 初始化数据库：
```bash
python init_db.py
```

6. 启动后端服务：
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 前端设置

1. 进入前端目录：
```bash
cd bb2y2b-vite-frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 访问应用：
打开浏览器访问 `http://localhost:5173`

## 使用说明

### 1. 配置B站Cookie

为了访问B站API，需要配置有效的Cookie：

1. 登录B站网页版
2. 打开开发者工具，复制Cookie中的SESSDATA值
3. 在项目根目录创建 `cookie.json` 文件：
```json
{
  "SESSDATA": "your_sessdata_value_here"
}
```

### 2. 添加UP主空间

1. 在"UP主空间管理"页面点击"添加空间"
2. 输入UP主的space_id（从UP主主页URL获取）
3. 设置视频类型和关键词过滤
4. 点击"扫描视频"获取最新视频列表

### 3. 下载视频

1. 在"视频管理"页面查看扫描到的视频
2. 点击"下载"按钮开始下载
3. 在"下载管理"页面查看下载进度
4. 下载完成后可以在线播放或查看AI字幕

## API文档

后端启动后，访问以下地址查看API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 开发说明

### 添加新功能

1. 后端：在 `app/api/v1/endpoints/` 添加新的API端点
2. 前端：在 `src/components/` 添加新的React组件
3. 数据库：使用Alembic创建数据库迁移

### 代码规范

- 后端：遵循PEP 8 Python代码规范
- 前端：使用ESLint和Prettier进行代码格式化
- 提交：使用语义化提交信息

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 注意事项

- 本项目仅供学习和个人使用
- 请遵守B站的使用条款和相关法律法规
- 下载的内容请勿用于商业用途