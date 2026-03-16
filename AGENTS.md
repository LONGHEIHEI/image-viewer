以下是给 Codex/自动化代理的项目指引，请在本仓库内工作时遵循。

**项目概览**
这是一个“轻图”Web 应用，前端为 Vue 3 + Vite + TypeScript + Naive UI，后端为 FastAPI + SQLite + Pillow。支持目录树浏览、图片分页、压缩包（ZIP/7Z/RAR）直读、缩略图缓存、用户与集合权限管理，以及 PWA 适配。

**仓库结构**
- `backend/`：FastAPI 服务端（鉴权、目录/压缩包索引、缩略图、用户/集合）
- `frontend/`：Vue 3 前端（登录、目录树、图片列表、预览器、管理后台）
- `docs/`：架构、API、部署文档
- `photos/`：本地图片与压缩包示例目录
- `cache/`：缩略图缓存目录

**后端关键路径**
- `backend/app/main.py`：服务入口与启动初始化
- `backend/app/api/`：路由与接口
- `backend/app/services/`：鉴权、DB、索引、缩略图、归档读取
- `backend/app/utils/path.py`：路径规范化与越界防护

**前端关键路径**
- `frontend/src/main.ts`、`frontend/src/App.vue`：入口与布局
- `frontend/src/router/index.ts`：路由与鉴权守卫
- `frontend/src/store/`：登录与图库状态
- `frontend/src/views/`：各页面
- `frontend/src/components/`：目录树、瀑布流、预览器等组件

**开发与运行**
- 后端：
  - `cd backend`
  - `python -m venv .venv`
  - `. .venv\Scripts\activate`
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8010`
- 前端：
  - `cd frontend`
  - `npm install`
  - `npm run dev`
- 默认管理账号：`admin` / `admin`

**编码与提交约束**
- 中文内容必须以 UTF-8 保存；必要时使用 PowerShell UTF-8 输出设置以避免乱码。
- 修改需尽量小而清晰，避免大范围重构。
- 与路径/权限相关的改动必须同步检查后端 `app/utils/path.py` 与权限过滤逻辑。

**常见功能链路**
- 登录：`POST /api/auth/login` 获取 JWT
- 目录树：`GET /api/tree`
- 目录分页：`GET /api/folder`
- 压缩包分页：`GET /api/archive`
- 图片/缩略图流：`/api/image`、`/api/thumb`，压缩包内使用 `/api/archive/*`
- 集合访问需先 `POST /api/collections/{id}/access` 获取集合 token
