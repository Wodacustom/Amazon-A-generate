# Amazon A+ 智能体 MVP

本仓库当前后端已重构为 MVP 版本，核心技术栈为 FastAPI、LangGraph、PostgreSQL + pgvector、Redis，以及兼容 S3 协议的 RustFS 对象存储。

## 后端接口

主要 API 路由：

- `GET /api/health`
- `POST /api/files`
- `POST /api/products`
- `POST /api/agent/runs`
- `GET /api/agent/runs/{run_id}`
- `GET /api/search?query=...`

## 本地检查

```powershell
uv pip install -r backend\requirements.txt
pytest -p no:cacheprovider backend\tests
docker compose -f docker\docker-compose.yml config
```

命令说明：

- `uv pip install -r backend\requirements.txt`：安装后端依赖。
- `pytest -p no:cacheprovider backend\tests`：运行后端测试，并避免写入 pytest 缓存。
- `docker compose -f docker\docker-compose.yml config`：校验 Docker Compose 配置是否可解析。

## 部署方式

### Docker 全栈部署

推荐本地或测试环境使用 Docker Compose 启动完整依赖栈：

```powershell
docker compose -f docker\docker-compose.yml up --build
```

默认服务端口：

- 前端：`http://localhost:5173`
- 后端：`http://localhost:8002`
- RustFS API：`http://localhost:9000`
- RustFS Console：`http://localhost:9001`

后端容器启动时会自动执行 `database/001_initial_mvp.sql`。该 SQL 会启用 PostgreSQL 的 `vector` 扩展，并创建 MVP 所需的数据表。

如果之前启动过旧数据库结构，需要清空 Docker volume 后重新启动：

```powershell
docker compose -f docker\docker-compose.yml down -v
docker compose -f docker\docker-compose.yml up --build
```

`down -v` 会删除 PostgreSQL、Redis、RustFS 的本地数据卷，执行前确认不需要保留旧数据。

### 后端单独部署

后端需要先准备 PostgreSQL + pgvector、Redis 和 RustFS/S3 兼容对象存储。安装依赖并启动：

```powershell
uv sync --dev
python -m app.db.apply_sql database\001_initial_mvp.sql
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

生产环境至少需要配置：

- `DATABASE_URL`
- `REDIS_URL`
- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET`
- `ALLOWED_ORIGINS`

启动后可检查：

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

### 前端单独部署

前端位于 `frontend/`，使用 Vue 3 + Vite。安装依赖、构建静态资源：

```powershell
cd frontend
pnpm install
pnpm run build
```

构建产物位于 `frontend/dist/`，可部署到 Nginx、对象存储静态站点或任意静态资源服务器。

如果前端和后端不同域名部署，需要设置：

```powershell
VITE_API_BASE_URL=https://your-api-domain.example.com/api
```

本地预览构建产物：

```powershell
pnpm run preview
```

## 项目结构

- `backend/app/`：FastAPI 后端源码，包含 API、schemas、services、agents、models、db 和 core 配置。
- `database/`：数据库初始化 SQL 脚本。
- `backend/tests/`：后端 pytest 测试。
- `frontend/src/`：Vue 前端源码。
- `docker/`：前后端 Dockerfile 与本地 Compose 编排。

## 配置说明

后端环境变量示例位于 `backend/.env.example`，Docker 环境变量示例位于 `docker/.env.example`。本地不要提交真实密钥；RustFS 访问凭据、S3 bucket、Redis、PostgreSQL 连接等都应通过环境变量配置。
