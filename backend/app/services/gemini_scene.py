from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.mockup import MockupRecommendationRequest
from app.services.qwen_scene import QwenSceneClient


class GeminiSceneClient:
    def recommend(self, payload: MockupRecommendationRequest) -> dict[str, Any] | None:
        if not settings.gemini_api_key:
            return None

        response_text = self._generate_content(payload)
        data = QwenSceneClient()._parse_json(response_text)
        if not data:
            return None
        return QwenSceneClient()._normalize(data)

    def _generate_content(self, payload: MockupRecommendationRequest) -> str:
        model = settings.gemini_model.strip().removeprefix("models/")
        url = f"{settings.gemini_base_url.rstrip('/')}/models/{model}:generateContent"
        body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                "你是电商 A+ 详情页视觉策划 Agent。"
                                "请基于商品资料判断产品类目、使用场景、样机提示词。"
                                "只输出严格 JSON，不要输出 Markdown。\n\n"
                                f"{self._build_user_prompt(payload)}"
                            )
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key.get_secret_value(),
        }

        with httpx.Client(timeout=settings.gemini_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()

        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "".join(str(part.get("text", "")) for part in parts)

    def _build_user_prompt(self, payload: MockupRecommendationRequest) -> str:
        info = payload.product_info
        return json.dumps(
            {
                "task": "recommend ecommerce product usage scenes and visual prompts",
                "outputSchema": {
                    "productCategory": "one of beauty, pet, outdoor, sports, electronics, kitchen, home",
                    "scenes": [
                        {
                            "id": "short snake_case scene id",
                            "name": "中文场景名称",
                            "category": "same as productCategory",
                            "audience": "目标人群",
                            "reason": "为什么适合这个产品",
                            "riskNotes": ["合规风险或画面风险"],
                            "prompt": {
                                "positive": "English image generation prompt for A+ ecommerce mockup",
                                "negative": "English negative prompt",
                                "composition": "构图要求",
                                "productPlacement": "产品融合和放置要求",
                                "supportingProps": ["道具"],
                            },
                        }
                    ],
                },
                "rules": [
                    "返回 2 到 3 个场景",
                    "不要使用绝对化、医疗化、夸大功效表达",
                    "提示词要强调产品主体清晰、Logo 不变形、可留文字安全区",
                    "positive/negative 使用英文，name/reason/riskNotes 可以使用中文",
                ],
                "product": {
                    "name": info.product_name,
                    "sellingPoints": info.core_selling_points,
                    "targetAudience": info.target_audience,
                    "useScenes": info.use_scenes,
                    "specifications": info.specifications,
                    "brandTone": info.brand_tone,
                    "forbiddenWords": info.forbidden_words,
                    "complianceNotes": info.compliance_notes,
                    "platform": payload.platform,
                    "country": payload.country,
                    "language": payload.language,
                    "imageRatio": payload.image_ratio,
                    "designStyle": payload.design_style,
                    "imageCount": len(payload.images),
                },
            },
            ensure_ascii=False,
        )
