# 轻图

一个轻量、文件夹优先的图片浏览器，支持 PWA 与 ZIP/7Z/RAR 直读。前端使用 Vue 3 + Naive UI，后端使用 FastAPI。

## 功能
- 按原始文件夹结构浏览
- 目录树导航（含压缩包）
- ZIP/7Z/RAR 压缩包内图片直读（无需解压）
- 图片流与缩略图缓存
- 统一的图片浏览区：普通文件夹、压缩包、图集图片区共用同一套头部/搜索/分页壳子
- 目录/压缩包/图集封面与图片卡片使用显式加载状态，命中缓存时也能正确移除占位图
- 隐私遮罩点击揭开后平滑过渡，避免卡片内容“跳动一下”
- 沉浸式查看器：全屏、缩放、拖拽、快捷键
- 登录与用户管理（权限控制访问目录）
- 品牌化登录页（Logo + 名称 + 简短说明）
- 集合功能：多个目录合并为一个集合，仍按文件夹显示，可设置访问密码
- 统一通知提示（右上角）
- PWA 适配移动端，并在检测到新版本资源后提供显式“刷新”按钮
- Docker 友好部署

## 技术栈
- 前端：Vue 3 + Vite + TypeScript + Pinia + Vue Router + Naive UI + PWA
- 后端：FastAPI + Pillow

## 本地调试（Windows）

### 1. 准备图片目录
在项目根目录新建 `photos`，放入图片或压缩包，例如：
```
photos/
  set1/
    a.jpg
    pack.zip
```

### 2. 启动后端
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 可选：不配置也能启动（会使用默认路径）
$env:PHOTO_ROOT="C:\Users\LSW\Desktop\项目\image-views\photos"
$env:THUMB_CACHE="C:\Users\LSW\Desktop\项目\image-views\cache"
$env:THUMB_SIZE="320"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8010 --reload
```

验证：
- `http://localhost:8010/health` 返回 `{"status":"ok"}`

### 3. 启动前端
```powershell
cd frontend
npm install
npm run dev
```

访问：
- `http://localhost:5173`
- 浏览器里模拟 PWA 外壳可直接访问 `http://localhost:5173/?pwa=1`
- 关闭这类模拟可访问 `http://localhost:5173/?pwa=0`，或直接新开一个标签页

PWA 行为补充：
- 独立窗口/PWA 安装态下，前端会使用 service worker 缓存静态资源
- 当检测到新的前端资源版本时，界面会显示“刷新”按钮，由用户决定何时切换到新版本
- 图片/封面卡片的占位图通过显式加载状态控制；即使浏览器直接命中缓存，也会在资源可用后移除占位层

### 4. 登录
默认管理员账号：
- 用户名：`admin`
- 密码：`admin`

登录后可在右上角进入“用户管理”配置可访问目录，也可进入“集合管理”配置集合。

## 本地调试（macOS/Linux）
```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# 可选环境变量
export PHOTO_ROOT="/abs/path/to/photos"
export THUMB_CACHE="/abs/path/to/cache"
export THUMB_SIZE=320

uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

- 以上 `.venv/bin/activate` 仅适用于 macOS/Linux 的 `bash`/`zsh`
- Windows PowerShell 请使用 `.\.venv\Scripts\Activate.ps1`

```bash
cd frontend
npm install
npm run dev
```

## 集合功能说明
- 集合用于把多个目录合并到一个入口中展示
- 集合内仍保持原文件夹结构
- 支持设置访问密码（密码正确后才可进入）

## 压缩包依赖
- ZIP：内置支持
- 7Z/RAR：需要安装完整依赖

完整依赖安装：
```bash
cd backend
pip install -r requirements-full.txt
```

一键安装脚本：
- `scripts/install-archive-deps.ps1`
- `scripts/install-archive-deps.sh`

## Docker 部署
```bash
docker compose up -d --build
```

访问：
- 前端：`http://localhost:8480`
- 健康检查：`http://localhost:8480/health`（兼容探针）
- API 健康检查：`http://localhost:8480/api/health`

说明：
- Docker 默认启动单个 `app` 容器（FastAPI 直接提供前端静态资源）
- 对外端口可通过环境变量 `IMAGE_VIEWS_PORT` 调整，例如：
  ```powershell
  $env:IMAGE_VIEWS_PORT="8290"
  docker compose up -d --build
  ```
  ```bash
  IMAGE_VIEWS_PORT=8290 docker compose up -d --build
  ```

PWA 图标说明：
- 当前仓库提供 `frontend/public/icon.png`、`frontend/public/favicon.ico` 与 `index.html` 中的 `apple-touch-icon`
- 部分桌面壳子/移动启动器对图标尺寸和 maskable 安全区要求更严格；若需要适配更多安装入口，建议补齐独立的 `192x192`、`512x512`、`maskable`、`apple-touch-icon` 资源，而不是全部复用同一张源图

## 中文乱码处理（重点）
1. **源文件保存为 UTF-8**（推荐 UTF-8 无 BOM）
2. **项目内置 .editorconfig / .gitattributes / .vscode/settings.json**，统一编码与换行
3. **Windows 终端切换 UTF-8 代码页**：
   ```powershell
   chcp 65001
   ```
4. **PowerShell 输出编码（可选）**：
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```
5. **Python 强制 UTF-8（可选）**：
   ```powershell
   $env:PYTHONUTF8="1"
   $env:PYTHONIOENCODING="utf-8"
   ```

如果使用 VS Code，请确认右下角编码为 `UTF-8`，且工作区已写入 UTF-8 默认编码设置。

## 环境变量
- `PHOTO_ROOT`：图片根目录（默认 `/data/photos`）
- `THUMB_CACHE`：缩略图缓存目录（默认 `/data/cache`）
- `THUMB_SIZE`：缩略图尺寸（默认 `320`）
- `DB_PATH`：SQLite 数据库路径（默认 `data/app.db`）
- `SECRET_KEY`：JWT 密钥（默认 `dev-secret-change-me`）
- `ADMIN_USERNAME`：默认管理员用户名（默认 `admin`）
- `ADMIN_PASSWORD`：默认管理员密码（默认 `admin`）

> Windows 上不配置环境变量也能启动，但默认路径会指向 `C:\data\photos` 等位置，建议明确配置。

## 文档
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/DEPLOYMENT.md`
