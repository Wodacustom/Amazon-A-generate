import type { GenerationSettings, PromptConfig } from '@/types/generation'

export const defaultGenerationSettings: GenerationSettings = {
  platform: 'amazon',
  country: 'US',
  language: 'en',
  qualityLevel: 'normal_a_plus',
  imageRatio: 'platform_default',
  imageModel: 'nanobanana_pro',
  designStyle: 'minimal',
}

export const imageModelOptions = [
  { key: 'nanobanana_pro', label: 'Nano Banana Pro', description: '默认生图模型，适合产品图融合、样机合成和服装换装。' },
  { key: 'gemini_3_pro_image', label: 'Gemini 3 Pro Image', description: '当前同样映射到 Gemini 图片生成接口。' },
]

export const defaultPromptConfig: PromptConfig = {
  visualStyle: ['minimal'],
  color: ['white_background'],
  composition: ['product_center'],
  copyTone: ['professional'],
  content: [],
  platform: [],
  negative: ['no_exaggerated_claims'],
}

export const defaultModules = ['hero', 'selling_points', 'usage_scene', 'comparison', 'faq']

export const moduleOptions = [
  { key: 'hero', label: '首屏主视觉', description: '产品主图、核心卖点和品牌调性' },
  { key: 'selling_points', label: '卖点拆解', description: '3-5 个核心利益点的图文模块' },
  { key: 'usage_scene', label: '使用场景', description: '展示典型用户和真实使用环境' },
  { key: 'comparison', label: '参数对比', description: '结构化对比规格和差异化优势' },
  { key: 'faq', label: 'FAQ', description: '常见疑问、合规说明和购买阻力处理' },
]

export const inspirationItems = [
  {
    title: '户外运动水壶',
    prompt: '耐摔保温运动水壶，适合露营、徒步和健身房使用，突出长效保温、防漏和轻量携带。',
    imageUrl: 'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=600&q=80',
  },
  {
    title: '无线降噪耳机',
    prompt: '无线蓝牙降噪耳机，面向通勤和办公人群，突出主动降噪、长续航和舒适佩戴。',
    imageUrl: 'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=600&q=80',
  },
  {
    title: '宠物智能喂食器',
    prompt: '自动宠物喂食器，支持定时定量、远程控制和防潮储粮，适合猫狗家庭。',
    imageUrl: 'https://images.unsplash.com/photo-1601758124510-52d02ddb7cbd?auto=format&fit=crop&w=600&q=80',
  },
  {
    title: '瑜伽垫',
    prompt: '环保防滑瑜伽垫，突出抓地力、回弹支撑和易清洁，适合家庭训练和健身房。',
    imageUrl: 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80',
  },
  {
    title: '家用美容仪',
    prompt: '便携式家用美容仪，强调温和护理、多模式切换和精致礼品感，避免医疗化表述。',
    imageUrl: 'https://images.unsplash.com/photo-1522338242992-e1a54906a8da?auto=format&fit=crop&w=600&q=80',
  },
]

export const templateItems = [
  { id: 'basic-a-plus', name: 'Amazon A+ 基础图文', category: '通用', modules: ['hero', 'selling_points', 'faq'] },
  { id: 'brand-story', name: '高级 A+ 品牌故事', category: '品牌', modules: ['hero', 'usage_scene', 'comparison'] },
  { id: 'comparison', name: '卖点对比模板', category: '3C / 家居', modules: ['comparison', 'selling_points'] },
  { id: 'scenario', name: '场景说明模板', category: '户外 / 宠物', modules: ['usage_scene', 'hero'] },
]
