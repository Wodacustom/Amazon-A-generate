"""模型厂商适配器。"""

from app.services.models.adapters.gemini import GeminiAdapter
from app.services.models.adapters.mock import MockAdapter
from app.services.models.adapters.openai import NewAPIAdapter, OpenAIAdapter, QwenAdapter, VLLMAdapter

__all__ = ["GeminiAdapter", "MockAdapter", "NewAPIAdapter", "OpenAIAdapter", "QwenAdapter", "VLLMAdapter"]
