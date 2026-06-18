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

## Docker 启动

```powershell
docker compose -f docker\docker-compose.yml up --build
```

后端容器启动时会自动执行 Alembic migration。当前 initial migration 会启用 PostgreSQL 的 `vector` 扩展，并创建 MVP 所需的数据表。

## 项目结构

- `backend/app/`：FastAPI 后端源码，包含 API、schemas、services、agents、models、db 和 core 配置。
- `backend/alembic/versions/`：数据库迁移脚本。
- `backend/tests/`：后端 pytest 测试。
- `frontend/src/`：Vue 前端源码。
- `docker/`：前后端 Dockerfile 与本地 Compose 编排。

## 配置说明

后端环境变量示例位于 `backend/.env.example`，Docker 环境变量示例位于 `docker/.env.example`。本地不要提交真实密钥；RustFS 访问凭据、S3 bucket、Redis、PostgreSQL 连接等都应通过环境变量配置。
