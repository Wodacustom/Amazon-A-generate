"""产品 A+ 内容生成的 LangGraph MVP 工作流。

当前实现使用 mock 逻辑，重点是固定状态结构和节点顺序，方便后续替换为真实 LLM。
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.core.config import settings


class AgentState(TypedDict, total=False):
    """LangGraph 在各节点之间传递的状态。"""

    product_input: dict
    uploaded_files: list[dict]
    retrieved_context: list[dict]
    analysis: dict
    content_modules: list[dict]
    image_prompts: list[dict]
    errors: list[str]


class ProductAgentGraph:
    """封装产品内容生成图，提供同步 run 接口给服务层调用。"""

    def __init__(self) -> None:
        """声明节点和边，并编译 LangGraph。"""
        graph = StateGraph(AgentState)
        graph.add_node("validate_input", self._validate_input)
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("analyze_product", self._analyze_product)
        graph.add_node("generate_content", self._generate_content)
        graph.add_node("generate_image_prompts", self._generate_image_prompts)
        graph.add_edge(START, "validate_input")
        graph.add_edge("validate_input", "retrieve_context")
        graph.add_edge("retrieve_context", "analyze_product")
        graph.add_edge("analyze_product", "generate_content")
        graph.add_edge("generate_content", "generate_image_prompts")
        graph.add_edge("generate_image_prompts", END)
        self._graph = graph.compile()

    def run(self, product_input: dict, retrieved_context: list[dict] | None = None) -> AgentState:
        """运行智能体图，返回包含内容模块和图片提示词的最终状态。"""
        return self._graph.invoke({"product_input": product_input, "retrieved_context": retrieved_context or []})

    def _validate_input(self, state: AgentState) -> AgentState:
        """校验最小必填输入。"""
        product = state.get("product_input") or {}
        errors = []
        if not product.get("name"):
            errors.append("Product name is required.")
        return {"errors": errors}

    def _retrieve_context(self, state: AgentState) -> AgentState:
        """透传服务层从 pgvector 检索出的上下文。"""
        return {"retrieved_context": state.get("retrieved_context", [])}

    def _analyze_product(self, state: AgentState) -> AgentState:
        """根据产品输入和检索上下文生成基础分析。"""
        product = state.get("product_input", {})
        selling_points = product.get("selling_points") or []
        context = state.get("retrieved_context", [])
        return {
            "analysis": {
                "positioning": f"{product.get('name', 'Product')} for {product.get('platform', 'amazon')}",
                "primary_benefits": selling_points[:5],
                "context_count": len(context),
            }
        }

    def _generate_content(self, state: AgentState) -> AgentState:
        """生成 MVP 版本的 A+ 内容模块。"""
        product = state.get("product_input", {})
        analysis = state.get("analysis", {})
        name = product.get("name", "Product")
        benefits = analysis.get("primary_benefits") or ["Reliable quality", "Simple daily use", "Clean presentation"]
        modules = [
            {
                "type": "hero",
                "title": f"{name} Built for Everyday Confidence",
                "subtitle": product.get("description") or "A clean Amazon A+ hero draft.",
                "body": "Highlight the product clearly with concise, compliant copy.",
            },
            {
                "type": "benefits",
                "title": "Key Benefits",
                "items": benefits,
            },
            {
                "type": "details",
                "title": "Product Details",
                "items": product.get("specs") or {},
            },
        ]
        return {"content_modules": modules}

    def _generate_image_prompts(self, state: AgentState) -> AgentState:
        """为每个内容模块生成图片提示词。"""
        product = state.get("product_input", {})
        modules = state.get("content_modules", [])
        image_prompts = [
            {
                "module_type": module["type"],
                "prompt": (
                    f"Amazon A+ module image for {product.get('name', 'product')}, "
                    f"{module.get('title', '')}, clean commercial product photography, text-safe composition"
                ),
            }
            for module in modules
        ]
        return {
            "image_prompts": image_prompts,
            "analysis": {
                **state.get("analysis", {}),
                "llm_provider": settings.llm_provider,
                "llm_model": settings.llm_model,
            },
        }
