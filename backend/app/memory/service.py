def summarize_context(messages: list[dict]) -> dict:
    return {"messageCount": len(messages), "latestInstruction": messages[-1]["content"] if messages else ""}
