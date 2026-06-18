"""智能体运行服务。

服务层负责数据库记录、Redis 进度缓存、pgvector 上下文检索，以及调用 LangGraph。
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import ProductAgentGraph
from app.models.agent import AgentResult, AgentRun
from app.models.product import Product
from app.schemas.agent import AgentRunCreate
from app.services.redis_client import get_redis
from app.services.vectorstore import VectorStore


class AgentRunner:
    """协调一次 agent run 的完整生命周期。"""

    def __init__(self, graph: ProductAgentGraph | None = None, vectorstore: VectorStore | None = None) -> None:
        """允许测试注入 graph 或 vectorstore。"""
        self.graph = graph or ProductAgentGraph()
        self.vectorstore = vectorstore or VectorStore()

    async def create_and_run(self, db: AsyncSession, payload: AgentRunCreate) -> tuple[AgentRun, AgentResult | None]:
        """创建运行记录并立即执行 MVP 智能体流程。"""
        product_input = await self._resolve_product_input(db, payload)
        run = AgentRun(product_id=payload.product_id, status="running", progress=10, current_step="retrieving_context", input_snapshot=product_input)
        db.add(run)
        await db.flush()
        await self._set_progress(run.id, 10, "retrieving_context")

        try:
            # 先从 pgvector 找相关历史上下文，再交给 LangGraph。
            context_docs = await self.vectorstore.search(db, self._document_text(product_input), limit=5)
            context = [
                {"source_type": doc.source_type, "source_id": doc.source_id, "content": doc.content, "metadata": doc.document_metadata}
                for doc in context_docs
            ]
            await self._set_progress(run.id, 35, "running_graph")
            state = self.graph.run(product_input, context)
            if state.get("errors"):
                raise ValueError("; ".join(state["errors"]))

            # LangGraph 结果落库，供查询接口和后续检索使用。
            result = AgentResult(
                run_id=run.id,
                product_id=payload.product_id,
                content_modules=state.get("content_modules", []),
                image_prompts=state.get("image_prompts", []),
                model_metadata={"analysis": state.get("analysis", {}), "retrieved_context": context},
            )
            db.add(result)
            await db.flush()
            await self.vectorstore.add_document(
                db,
                source_type="agent_result",
                source_id=str(result.id),
                content=self._result_text(result),
                metadata={"run_id": str(run.id), "product_id": str(payload.product_id) if payload.product_id else None},
            )
            run.status = "completed"
            run.progress = 100
            run.current_step = "completed"
            await self._set_progress(run.id, 100, "completed")
            await db.commit()
            await db.refresh(run)
            await db.refresh(result)
            return run, result
        except Exception as exc:
            # MVP 阶段直接把错误写入 run，方便前端轮询展示。
            run.status = "failed"
            run.progress = 100
            run.current_step = "failed"
            run.error_message = str(exc)
            await db.commit()
            await self._set_progress(run.id, 100, "failed")
            return run, None

    async def get_result_for_run(self, db: AsyncSession, run_id: UUID) -> AgentResult | None:
        """按运行 ID 查询结果记录。"""
        result = await db.execute(select(AgentResult).where(AgentResult.run_id == run_id))
        return result.scalar_one_or_none()

    async def _resolve_product_input(self, db: AsyncSession, payload: AgentRunCreate) -> dict:
        """合并产品表数据和请求里临时覆盖的输入。"""
        if payload.product_id is None:
            return payload.product_input
        product = await db.get(Product, payload.product_id)
        if product is None:
            raise ValueError("Product not found.")
        data = {
            "id": str(product.id),
            "name": product.name,
            "platform": product.platform,
            "country": product.country,
            "language": product.language,
            "selling_points": product.selling_points,
            "specs": product.specs,
            "description": product.description,
            "file_ids": product.file_ids,
        }
        data.update(payload.product_input)
        return data

    async def _set_progress(self, run_id: UUID, progress: int, step: str) -> None:
        """把短期进度写入 Redis；Redis 不可用时不影响主流程。"""
        try:
            await get_redis().hset(f"agent_run:{run_id}", mapping={"progress": progress, "step": step})
            await get_redis().expire(f"agent_run:{run_id}", 3600)
        except Exception:
            return

    def _document_text(self, product_input: dict) -> str:
        """把产品输入压平成可 embedding 的文本。"""
        return " ".join(
            [
                str(product_input.get("name", "")),
                str(product_input.get("description", "")),
                " ".join(product_input.get("selling_points") or []),
                str(product_input.get("specs") or {}),
            ]
        )

    def _result_text(self, result: AgentResult) -> str:
        """把生成结果压平成可写入向量库的文本。"""
        chunks = []
        for module in result.content_modules:
            chunks.append(str(module.get("title", "")))
            chunks.append(str(module.get("body", "")))
            chunks.append(str(module.get("items", "")))
        return " ".join(chunks)
