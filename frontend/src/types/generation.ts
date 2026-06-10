import type { ProductInfo } from './product'
import type { MockupGenerationPlan } from './mockup'

export interface GenerationSettings {
  platform: string
  country: string
  language: string
  qualityLevel: string
  imageRatio: string
  imageModel: string
  designStyle: string
}

export interface PromptConfig {
  visualStyle: string[]
  color: string[]
  composition: string[]
  copyTone: string[]
  content: string[]
  platform: string[]
  negative: string[]
}

export type StyleMemoryMode = 'none' | 'user' | 'company' | 'brand'

export interface StyleMemorySelection {
  mode: StyleMemoryMode
  memoryId?: string
  updateAfterGeneration: boolean
}

export interface PromptOption {
  key: string
  label: string
  prompt: string
  negative: boolean
}

export interface PromptOptionGroup {
  key: keyof PromptConfig // 等价于 key: 'visualStyle' | 'color' | 'composition' | 'copyTone' | 'content' | 'platform' | 'negative'
  label: string
  selection: 'single' | 'multiple'
  options: PromptOption[]
}

export interface CreateGenerationTaskPayload {
  productId?: string
  images: string[]
  platform: string
  country: string
  language: string
  qualityLevel: string
  imageRatio: string
  imageModel: string
  designStyle: string
  productInfo: ProductInfo
  modules: string[]
  promptConfig: PromptConfig
  styleMemory: StyleMemorySelection
  mockupPlan?: MockupGenerationPlan
}

export interface GenerationTask {
  id: string
  productName: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled' | string
  progress: number
  currentStep: string
  createdAt: string
  errorMessage?: string
  conversationSessionId?: string
}

export interface GenerationProgressStep {
  key: string
  label: string
  detail: string
  percentage: number
}
