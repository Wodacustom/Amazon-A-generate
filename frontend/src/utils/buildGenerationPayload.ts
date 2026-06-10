import type {
  CreateGenerationTaskPayload,
  GenerationSettings,
  PromptConfig,
  StyleMemorySelection,
} from '@/types/generation'
import type { MockupGenerationPlan } from '@/types/mockup'
import type { ProductImage, ProductInfo } from '@/types/product'

export function buildGenerationPayload(
  productId: string | undefined,
  images: ProductImage[],
  settings: GenerationSettings,
  productInfo: ProductInfo,
  modules: string[],
  promptConfig: PromptConfig,
  styleMemory: StyleMemorySelection,
  mockupPlan?: MockupGenerationPlan,
): CreateGenerationTaskPayload {
  return {
    productId,
    images: images.filter((image) => image.uploadStatus === 'success').map((image) => image.url),
    platform: settings.platform,
    country: settings.country,
    language: settings.language,
    qualityLevel: settings.qualityLevel,
    imageRatio: settings.imageRatio,
    imageModel: settings.imageModel,
    designStyle: settings.designStyle,
    productInfo,
    modules,
    promptConfig,
    styleMemory,
    mockupPlan,
  }
}
