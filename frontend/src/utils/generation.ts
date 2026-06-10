export { buildGenerationPayload } from './buildGenerationPayload'
export { promptConfigToText } from './prompt'
export { validateGenerationDraft } from './validation'

import type { GenerationResult } from '@/types/result'

export function createMockResult(taskId: string, productId: string, productName: string, modules: string[]): GenerationResult {
  return {
    id: `result-${taskId}`,
    taskId,
    productId,
    qualityScore: 86,
    exportUrls: {},
    metadata: { source: 'local-mock' },
    modules: modules.map((module, index) => ({
      id: `${taskId}-${module}`,
      type: module,
      title: `${productName} ${moduleTitle(module)}`,
      subtitle: index === 0 ? 'AI 生成的 A+ 模块草稿' : undefined,
      description: '围绕商品卖点、使用场景和平台合规要求生成的模块内容。',
      imageUrl: undefined,
      layout: module === 'hero' ? 'wide' : 'split',
      sortOrder: index,
    })),
  }
}

function moduleTitle(module: string) {
  const titles: Record<string, string> = {
    full_aplus_mockup: '整页 A+ 样机图',
    hero: '主视觉',
    selling_points: '卖点拆解',
    scenario: '使用场景',
    usage_scene: '使用场景',
    comparison: '参数对比',
    faq: 'FAQ',
  }
  return titles[module] || module
}
