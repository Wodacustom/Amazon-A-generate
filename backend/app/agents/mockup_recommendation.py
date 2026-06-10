from app.core.config import settings
from app.schemas.mockup import MockupRecommendationRequest
from app.services.gemini_scene import GeminiSceneClient
from app.services.mockup_repository import list_mockup_templates
from app.services.qwen_scene import QwenSceneClient


class MockupRecommendationAgent:
    def __init__(
        self,
        qwen_client: QwenSceneClient | None = None,
        gemini_client: GeminiSceneClient | None = None,
    ) -> None:
        self.qwen_client = qwen_client or QwenSceneClient()
        self.gemini_client = gemini_client or GeminiSceneClient()

    def run(self, payload: MockupRecommendationRequest) -> dict:
        product_text = " ".join(
            [
                payload.product_info.product_name,
                payload.product_info.core_selling_points,
                payload.product_info.target_audience,
                payload.product_info.use_scenes,
                payload.product_info.specifications,
            ]
        ).lower()
        product_category = self._detect_category(product_text)
        scenes = self._recommend_scenes(payload, product_category)
        llm_result = self._recommend_with_llm(payload)
        if llm_result:
            product_category = llm_result["productCategory"]
            scenes = llm_result["scenes"]
        matched = self._match_mockups(product_category, scenes, payload.platform, payload.image_ratio)
        selected_plan = self._build_plan(scenes, matched)

        return {
            "productCategory": product_category,
            "scenes": scenes,
            "matchedMockups": matched,
            "selectedPlan": selected_plan,
        }

    def _recommend_with_llm(self, payload: MockupRecommendationRequest) -> dict | None:
        try:
            if settings.scene_agent_provider == "qwen":
                return self.qwen_client.recommend(payload)
            if settings.scene_agent_provider == "gemini":
                return self.gemini_client.recommend(payload)
            return None
        except Exception:
            return None

    def _detect_category(self, text: str) -> str:
        rules = [
            ("beauty", ["beauty", "skincare", "makeup", "cosmetic", "美容", "护肤", "美妆"]),
            ("pet", ["pet", "cat", "dog", "宠物", "猫", "狗"]),
            ("outdoor", ["outdoor", "camping", "hiking", "travel", "户外", "露营", "旅行"]),
            ("sports", ["fitness", "gym", "yoga", "training", "sports", "健身", "运动", "瑜伽"]),
            ("electronics", ["wireless", "usb", "bluetooth", "charger", "earbuds", "电子", "蓝牙"]),
            ("kitchen", ["kitchen", "coffee", "grinder", "bottle", "cup", "厨房", "咖啡", "水杯"]),
        ]
        for category, keywords in rules:
            if any(keyword in text for keyword in keywords):
                return category
        return "home"

    def _recommend_scenes(self, payload: MockupRecommendationRequest, category: str) -> list[dict]:
        product_name = payload.product_info.product_name or "the product"
        audience = payload.product_info.target_audience or "target shoppers"
        explicit_scene = payload.product_info.use_scenes.strip()

        presets = {
            "beauty": [
                ("vanity", "梳妆台护理场景", "突出精致感、礼品感和日常护理氛围", ["mirror", "towel", "soft daylight"]),
                ("gift", "礼品开箱场景", "适合强调包装质感和送礼属性", ["gift box", "ribbon", "clean background"]),
            ],
            "pet": [
                ("pet_care", "宠物家庭护理场景", "让买家快速理解宠物和主人如何使用", ["living room", "pet bowl", "soft rug"]),
                ("daily_use", "日常居家场景", "降低理解成本，增强真实使用代入感", ["home interior", "warm light"]),
            ],
            "outdoor": [
                ("camping", "户外露营场景", "适合展示便携、耐用和旅途使用价值", ["tent", "backpack", "wood table"]),
                ("travel", "旅行通勤场景", "强化移动使用和轻量化优势", ["carry bag", "car interior", "daylight"]),
            ],
            "sports": [
                ("gym", "健身房训练场景", "突出运动过程中的便利性和强度感", ["fitness mat", "dumbbell", "water bottle"]),
                ("training", "居家训练场景", "适合展示家庭用户的低门槛使用", ["yoga mat", "clean floor"]),
            ],
            "electronics": [
                ("office", "办公桌面场景", "适合展示效率、专业感和设备搭配", ["laptop", "notebook", "desk lamp"]),
                ("travel", "通勤旅行场景", "突出便携、续航或收纳价值", ["backpack", "phone", "train table"]),
            ],
            "kitchen": [
                ("kitchen", "厨房台面场景", "适合展示烹饪、冲泡或收纳的真实位置", ["wood countertop", "cup", "clean utensil"]),
                ("daily_use", "日常早餐场景", "让功能卖点融入家庭生活节奏", ["breakfast plate", "window light"]),
            ],
            "home": [
                ("daily_use", "居家日用场景", "用真实环境说明产品价值和尺寸感", ["living room", "neutral props"]),
                ("gift", "礼品氛围场景", "适合强调质感、包装和购买理由", ["gift box", "clean tabletop"]),
            ],
        }

        candidates = presets.get(category, presets["home"])
        if explicit_scene:
            candidates = [("user_scene", explicit_scene, "来自商品资料的指定使用场景，优先保留美工意图", [])] + candidates

        scenes = []
        for scene_id, name, reason, props in candidates[:3]:
            scenes.append(
                {
                    "id": scene_id,
                    "name": name,
                    "category": category,
                    "audience": audience,
                    "reason": reason,
                    "riskNotes": ["避免夸大功效或绝对化承诺", "保持产品主体、Logo 和包装文字不变形"],
                    "prompt": {
                        "positive": (
                            f"Commercial ecommerce A+ image for {product_name}, {name}, "
                            f"premium realistic product photography, natural lighting, clean composition, "
                            f"for {audience}, sharp product details"
                        ),
                        "negative": "distorted product, extra logo, unreadable text, exaggerated claims, medical claims, messy background",
                        "composition": "Leave clear text-safe space and keep the product as the visual focus.",
                        "productPlacement": (
                            "Use the selected mockup image as the scene template. Replace the product shown in the "
                            "mockup with the user's original product while preserving the user's product shape, logo, "
                            "label text, packaging details, and proportions. Match the mockup perspective, lighting, "
                            "contact shadow, reflections, and depth of field."
                        ),
                        "supportingProps": props,
                    },
                }
            )
        return scenes

    def _match_mockups(
        self,
        category: str,
        scenes: list[dict],
        platform: str,
        image_ratio: str | None,
    ) -> list[dict]:
        scene_ids = {scene["id"] for scene in scenes}
        matched = []
        for template in list_mockup_templates():
            score = 40
            if category in template["category"]:
                score += 25
            if scene_ids.intersection(template["scenes"]):
                score += 20
            if platform in template["platforms"]:
                score += 10
            if image_ratio and image_ratio in template["ratios"]:
                score += 5

            best_scene_id = next((scene["id"] for scene in scenes if scene["id"] in template["scenes"]), scenes[0]["id"])
            matched.append(
                {
                    "template": template,
                    "sceneId": best_scene_id,
                    "score": min(score, 100),
                    "reason": "类目、使用场景、平台和比例匹配度综合排序",
                }
            )
        return sorted(matched, key=lambda item: item["score"], reverse=True)[:4]

    def _build_plan(self, scenes: list[dict], matched: list[dict]) -> dict | None:
        if not scenes or not matched:
            return None
        selected_scene = next((scene for scene in scenes if scene["id"] == matched[0]["sceneId"]), scenes[0])
        return {
            "sceneId": selected_scene["id"],
            "templateId": matched[0]["template"]["id"],
            "template": matched[0]["template"],
            "matchScore": matched[0]["score"],
            "scenePrompt": selected_scene["prompt"],
            "compositionNotes": (
                f"Use {matched[0]['template']['name']} as the mockup template. "
                "Ask the image model to replace the product in the mockup with the user's original product, then harmonize perspective, color temperature, lighting, and shadow."
            ),
        }
