# Image Views 写真浏览器

一个轻量、文件夹优先的写真浏览器，支持 PWA 与 ZIP/7Z/RAR 直读。前端使用 Vue 3 + Naive UI，后端使用 FastAPI。

## 功能
- 按原始文件夹结构浏览
- 目录树导航（含压缩包）
- ZIP/7Z/RAR 压缩包内图片直读（无需解压）
- 图片流与缩略图缓存
- 沉浸式查看器：全屏、缩放、拖拽、快捷键
- 登录与用户管理（权限控制访问目录）
- 集合功能：多个目录合并为一个集合，仍按文件夹显示，可设置访问密码
- 统一通知提示（右上角）
- PWA 适配移动端
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
. .venv\Scripts\activate
pip install -r requirements.txt

# 可选：不配置也能启动（会使用默认路径）
$env:PHOTO_ROOT="C:\Users\LSW\Desktop\项目\image-views\photos"
$env:THUMB_CACHE="C:\Users\LSW\Desktop\项目\image-views\cache"
$env:THUMB_SIZE="320"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
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
cd docker
docker compose up -d --build
```

访问：
- 前端：`http://localhost:8080`
- 后端健康检查：`http://localhost:8010/health`

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
