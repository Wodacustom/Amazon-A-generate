from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.core.config import settings


class AgentState(TypedDict, total=False):
    product_input: dict
    uploaded_files: list[dict]
    retrieved_context: list[dict]
    analysis: dict
    content_modules: list[dict]
    image_prompts: list[dict]
    errors: list[str]


class ProductAgentGraph:
    def __init__(self) -> None:
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
        return self._graph.invoke({"product_input": product_input, "retrieved_context": retrieved_context or []})

    def _validate_input(self, state: AgentState) -> AgentState:
        product = state.get("product_input") or {}
        errors = []
        if not product.get("name"):
            errors.append("Product name is required.")
        return {"errors": errors}

    def _retrieve_context(self, state: AgentState) -> AgentState:
        return {"retrieved_context": state.get("retrieved_context", [])}

    def _analyze_product(self, state: AgentState) -> AgentState:
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
