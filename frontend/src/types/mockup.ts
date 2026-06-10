import type { ProductInfo } from './product'

export interface ReplaceableArea {
  id: string
  type: string
  x: number
  y: number
  width: number
  height: number
}

export interface MockupTemplate {
  id: string
  name: string
  category: string[]
  scenes: string[]
  platforms: string[]
  ratios: string[]
  composition: string
  replaceableAreas: ReplaceableArea[]
  previewUrl: string
  sourceUrl: string
  tags: string[]
}

export interface ScenePrompt {
  positive: string
  negative: string
  composition: string
  productPlacement: string
  supportingProps: string[]
}

export interface SceneRecommendation {
  id: string
  name: string
  category: string
  audience: string
  reason: string
  riskNotes: string[]
  prompt: ScenePrompt
}

export interface MatchedMockup {
  template: MockupTemplate
  sceneId: string
  score: number
  reason: string
}

export interface MockupGenerationPlan {
  sceneId: string
  templateId: string
  template?: MockupTemplate
  matchScore?: number
  scenePrompt: ScenePrompt
  compositionNotes: string
}

export interface MockupRecommendationRequest {
  productInfo: ProductInfo
  images: string[]
  platform: string
  country: string
  language: string
  imageRatio?: string
  designStyle?: string
}

export interface MockupRecommendationResponse {
  productCategory: string
  scenes: SceneRecommendation[]
  matchedMockups: MatchedMockup[]
  selectedPlan?: MockupGenerationPlan
}
