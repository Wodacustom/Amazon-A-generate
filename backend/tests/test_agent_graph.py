"""LangGraph MVP 工作流测试。"""

import asyncio

from app.agents import ProductAgentGraph


def test_product_agent_graph_generates_mvp_content():
    """验证 mock 工作流能输出基础 A+ 模块和图片提示词。"""
    state = asyncio.run(
        ProductAgentGraph().run(
            {
                "name": "Portable Coffee Grinder",
                "platform": "amazon",
                "description": "Compact grinder for travel.",
                "selling_points": ["USB-C charging", "Easy to clean"],
                "specs": {"weight": "250g"},
            },
            [{"source_type": "product", "source_id": "demo", "content": "coffee context", "metadata": {}}],
        )
    )

    assert state["analysis"]["context_count"] == 1
    assert [module["type"] for module in state["content_modules"]] == ["hero", "benefits", "details"]
    assert state["image_prompts"][0]["module_type"] == "hero"
    assert state["analysis"]["embedding_dimensions"] == 1536
