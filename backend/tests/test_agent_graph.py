from app.agents import ProductAgentGraph


def test_product_agent_graph_generates_mvp_content():
    state = ProductAgentGraph().run(
        {
            "name": "Portable Coffee Grinder",
            "platform": "amazon",
            "description": "Compact grinder for travel.",
            "selling_points": ["USB-C charging", "Easy to clean"],
            "specs": {"weight": "250g"},
        },
        [{"source_type": "product", "source_id": "demo", "content": "coffee context", "metadata": {}}],
    )

    assert state["analysis"]["context_count"] == 1
    assert [module["type"] for module in state["content_modules"]] == ["hero", "benefits", "details"]
    assert state["image_prompts"][0]["module_type"] == "hero"
