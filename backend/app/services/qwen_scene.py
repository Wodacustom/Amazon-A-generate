from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings
from app.schemas.mockup import MockupRecommendationRequest


class QwenSceneClient:
    def recommend(self, payload: MockupRecommendationRequest) -> dict[str, Any] | None:
        if not settings.dashscope_api_key:
            return None

        response_text = self._chat_completion(payload)
        data = self._parse_json(response_text)
        if not data:
            return None
        return self._normalize(data)

    def _chat_completion(self, payload: MockupRecommendationRequest) -> str:
        url = f"{settings.dashscope_base_url.rstrip('/')}/chat/completions"
        body = {
            "model": settings.dashscope_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是电商 A+ 详情页视觉策划 Agent。"
                        "请基于商品资料判断产品类目、使用场景、样机提示词。"
                        "只输出严格 JSON，不要输出 Markdown。"
                    ),
                },
                {"role": "user", "content": self._build_user_prompt(payload)},
            ],
            "temperature": 0.3,
        }
        headers = {
            "Authorization": f"Bearer {settings.dashscope_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=settings.dashscope_timeout_seconds) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]

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

    def _parse_json(self, content: str) -> dict[str, Any] | None:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any] | None:
        category = str(data.get("productCategory") or "home")
        scenes = data.get("scenes")
        if not isinstance(scenes, list) or not scenes:
            return None

        normalized_scenes = []
        for index, scene in enumerate(scenes[:3]):
            if not isinstance(scene, dict):
                continue
            prompt = scene.get("prompt") if isinstance(scene.get("prompt"), dict) else {}
            normalized_scenes.append(
                {
                    "id": str(scene.get("id") or f"qwen_scene_{index + 1}"),
                    "name": str(scene.get("name") or "推荐使用场景"),
                    "category": str(scene.get("category") or category),
                    "audience": str(scene.get("audience") or "target shoppers"),
                    "reason": str(scene.get("reason") or "基于商品资料推荐的使用场景"),
                    "riskNotes": self._string_list(scene.get("riskNotes"))
                    or ["避免夸大功效或绝对化承诺", "保持产品主体、Logo 和包装文字不变形"],
                    "prompt": {
                        "positive": str(prompt.get("positive") or ""),
                        "negative": str(prompt.get("negative") or ""),
                        "composition": str(prompt.get("composition") or "Keep the product as the visual focus."),
                        "productPlacement": str(prompt.get("productPlacement") or "Place product naturally in the scene."),
                        "supportingProps": self._string_list(prompt.get("supportingProps")),
                    },
                }
            )

        if not normalized_scenes:
            return None
        return {"productCategory": category, "scenes": normalized_scenes}

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if item]
