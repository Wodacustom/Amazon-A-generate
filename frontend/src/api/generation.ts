// MVP 接口适配层：保留旧前端的 generation API 函数名，内部转调新后端 /agent/runs。
import { request } from './request'
import { toMvpProductPayload } from './product'

import type { CreateGenerationTaskPayload, GenerationTask } from '@/types/generation'
import type { GeneratedModule, GenerationResult, ResultVersion } from '@/types/result'

interface MvpProduct {
  // 新后端 /products 创建产品后返回的最小字段。
  id: string
}

interface MvpAgentResult {
  // 新后端 agent result 使用 snake_case，这里先按后端原始响应描述。
  id: string
  run_id: string
  product_id: string | null
  content_modules: Array<Record<string, unknown>>
  image_prompts: Array<{ module_type?: string; prompt?: string }>
  model_metadata: Record<string, unknown>
  created_at: string
}

interface MvpAgentRun {
  // 新后端 /agent/runs 返回一次 LangGraph 运行状态和结果。
  id: string
  product_id: string | null
  status: string
  progress: number
  current_step: string | null
  input_snapshot: Record<string, unknown>
  error_message: string | null
  result: MvpAgentResult | null
  created_at: string
  updated_at: string | null
}

export async function createGenerationTask(payload: CreateGenerationTaskPayload) {
  // 旧前端允许没有 productId；MVP 后端要求先有产品，所以这里自动补创建产品。
  const productId = payload.productId || (await createMvpProduct(payload)).id
  const { data } = await request.post<MvpAgentRun>(
    '/agent/runs',
    {
      product_id: productId,
      product_input: toAgentProductInput(payload),
    },
    {
      timeout: 300000,
    },
  )
  return mapRunToTask(data, payload.productInfo.productName)
}

export async function getGenerationTask(taskId: string) {
  // 旧前端保留“任务”概念，这里把 agent run 映射成 GenerationTask。
  const { data } = await request.get<MvpAgentRun>(`/agent/runs/${taskId}`)
  return mapRunToTask(data)
}

export async function getGenerationResult(taskId: string) {
  // MVP 后端通过 run 查询结果，前端仍按旧 result 类型消费。
  const { data } = await request.get<MvpAgentRun>(`/agent/runs/${taskId}`, {
    timeout: 60000,
  })
  if (!data.result) {
    throw new Error(data.error_message || '生成结果尚未完成')
  }
  return mapRunToResult(data)
}

export async function updateGenerationResult(resultId: string, payload: Partial<GenerationResult> & { versionLabel?: string }) {
  // MVP 后端暂未提供结果编辑持久化接口，先返回前端本地编辑后的结果。
  void resultId
  return payload as GenerationResult
}

export async function listResultVersions(resultId: string) {
  // MVP 后端暂未提供版本历史接口。
  void resultId
  return [] as ResultVersion[]
}

export async function createResultVersion(resultId: string, label = '手动保存') {
  // MVP 后端暂未提供版本保存接口，返回本地占位版本供 UI 使用。
  return {
    id: `local-version-${Date.now()}`,
    resultId,
    version: 1,
    label,
    createdAt: new Date().toISOString(),
    modules: [],
    exportUrls: {},
    qualityScore: 0,
    metadata: { source: 'mvp-local' },
  } satisfies ResultVersion
}

export async function restoreResultVersion(resultId: string, versionId: string) {
  void versionId
  throw new Error(`MVP 暂不支持恢复版本：${resultId}`)
}

async function createMvpProduct(payload: CreateGenerationTaskPayload) {
  // 将旧生成 payload 中的 productInfo 转成新后端 products 表结构。
  const { data } = await request.post<MvpProduct>(
    '/products',
    toMvpProductPayload(payload.productInfo, {
      platform: payload.platform,
      country: payload.country,
      language: payload.language,
      fileIds: payload.images,
    }),
  )
  return data
}

function toAgentProductInput(payload: CreateGenerationTaskPayload) {
  // LangGraph 节点读取的是扁平产品输入，旧前端的高级配置先放进 specs。
  return {
    name: payload.productInfo.productName || '未命名商品',
    platform: payload.platform,
    country: payload.country,
    language: payload.language,
    description: payload.productInfo.useScenes || payload.productInfo.coreSellingPoints,
    selling_points: splitSellingPoints(payload.productInfo.coreSellingPoints),
    specs: {
      targetAudience: payload.productInfo.targetAudience,
      useScenes: payload.productInfo.useScenes,
      specifications: payload.productInfo.specifications,
      brandTone: payload.productInfo.brandTone,
      forbiddenWords: payload.productInfo.forbiddenWords,
      complianceNotes: payload.productInfo.complianceNotes,
      qualityLevel: payload.qualityLevel,
      imageRatio: payload.imageRatio,
      imageModel: payload.imageModel,
      designStyle: payload.designStyle,
      modules: payload.modules,
      promptConfig: payload.promptConfig,
      styleMemory: payload.styleMemory,
      mockupPlan: payload.mockupPlan,
    },
    file_ids: payload.images,
  }
}

function mapRunToTask(run: MvpAgentRun, productName?: string): GenerationTask {
  // 后端 snake_case 字段转换成旧前端 camelCase task 字段。
  return {
    id: run.id,
    productName: productName || readString(run.input_snapshot.name),
    status: run.status,
    progress: run.progress,
    currentStep: run.current_step || run.status,
    createdAt: run.created_at,
    errorMessage: run.error_message || undefined,
    resultId: run.result?.id,
  }
}

function mapRunToResult(run: MvpAgentRun): GenerationResult {
  // 把新后端 result 映射成预览画布已有的 GenerationResult。
  const result = run.result
  if (!result) {
    throw new Error('生成结果不存在')
  }
  return {
    id: result.id,
    taskId: run.id,
    productId: result.product_id || run.product_id || '',
    modules: result.content_modules.map((module, index) => mapModule(module, index, result.image_prompts)),
    previewUrl: undefined,
    exportUrls: {},
    qualityScore: 86,
    metadata: result.model_metadata,
  }
}

function mapModule(module: Record<string, unknown>, index: number, imagePrompts: MvpAgentResult['image_prompts']): GeneratedModule {
  // 后端模块结构较自由，这里补齐前端预览组件必须字段。
  const type = readString(module.type) || `module_${index + 1}`
  const prompt = imagePrompts.find((item) => item.module_type === type)?.prompt
  return {
    id: `${type}-${index + 1}`,
    type,
    title: readString(module.title) || moduleTitle(type),
    subtitle: readString(module.subtitle),
    description: readString(module.body) || stringifyItems(module.items),
    visualPrompt: prompt,
    layout: type === 'hero' ? 'wide' : 'split',
    sortOrder: index,
  }
}

function splitSellingPoints(value: string) {
  // 兼容中文/英文分隔符，便于用户直接粘贴卖点文本。
  return value
    .split(/[;；,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function readString(value: unknown) {
  // 防止后端自由 JSON 字段把非字符串传入 Vue 文本区域。
  return typeof value === 'string' ? value : ''
}

function stringifyItems(value: unknown) {
  // benefits/details 模块可能返回数组或对象，统一转成展示文本。
  if (!value) return ''
  if (Array.isArray(value)) return value.join('；')
  if (typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key}: ${item}`).join('；')
  return String(value)
}

function moduleTitle(module: string) {
  // MVP 后端模块名和旧前端模块名不同，这里提供中文标题兜底。
  const titles: Record<string, string> = {
    hero: '主视觉',
    benefits: '卖点拆解',
    details: '产品详情',
  }
  return titles[module] || module
}
