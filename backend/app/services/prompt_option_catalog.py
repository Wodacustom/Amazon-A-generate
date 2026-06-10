PROMPT_OPTION_GROUPS = [
    {
        "key": "visual_style",
        "label": "视觉风格",
        "options": [
            {"key": "minimal", "label": "简约", "prompt": "clean minimal ecommerce design"},
            {"key": "premium_business", "label": "高端商务", "prompt": "premium business visual style"},
            {"key": "tech", "label": "科技感", "prompt": "modern technology aesthetic"},
            {"key": "parenting_soft", "label": "母婴柔和", "prompt": "soft family friendly visual tone"},
        ],
    },
    {
        "key": "color",
        "label": "色彩倾向",
        "options": [
            {"key": "white_background", "label": "白底", "prompt": "white background with enough whitespace"},
            {"key": "black_gold", "label": "黑金", "prompt": "black and gold premium palette"},
            {"key": "warm", "label": "暖色", "prompt": "warm low saturation colors"},
            {"key": "brand_first", "label": "品牌色优先", "prompt": "use brand color as primary accent"},
        ],
    },
    {
        "key": "composition",
        "label": "构图方式",
        "options": [
            {"key": "product_center", "label": "产品居中", "prompt": "center product composition"},
            {"key": "large_whitespace", "label": "大留白", "prompt": "large whitespace around product"},
            {"key": "left_text_right_image", "label": "左文右图", "prompt": "left copy and right product layout"},
            {"key": "scenario", "label": "场景化", "prompt": "realistic usage scenario composition"},
        ],
    },
    {
        "key": "copy_tone",
        "label": "文案语气",
        "options": [
            {"key": "professional", "label": "专业", "prompt": "professional and clear copywriting"},
            {"key": "restrained", "label": "克制", "prompt": "restrained claim-safe wording"},
            {"key": "conversion", "label": "转化导向", "prompt": "benefit-led conversion copy"},
        ],
    },
    {
        "key": "negative",
        "label": "禁用元素",
        "options": [
            {"key": "no_people", "label": "不要真人", "prompt": "no real people", "negative": True},
            {"key": "no_cartoon", "label": "不要卡通", "prompt": "no cartoon style", "negative": True},
            {"key": "no_complex_background", "label": "不要复杂背景", "prompt": "no complex background", "negative": True},
            {"key": "no_exaggerated_claims", "label": "不要夸张营销词", "prompt": "no exaggerated claims", "negative": True},
        ],
    },
]
