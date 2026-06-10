import { describe, expect, it } from 'vitest'

import { defaultGenerationSettings, defaultPromptConfig } from '@/data/options'
import type { ProductImage, ProductInfo } from '@/types/product'
import { buildGenerationPayload, createMockResult } from '@/utils/generation'
import { validateGenerationDraft } from '@/utils/validation'

const productInfo: ProductInfo = {
  productName: 'Test Grinder',
  coreSellingPoints: 'Portable; Durable',
  targetAudience: '',
  useScenes: '',
  specifications: '',
  brandTone: '',
  forbiddenWords: '',
  complianceNotes: '',
}

const images: ProductImage[] = [
  {
    id: 'image-1',
    url: 'https://example.com/image.jpg',
    type: 'main',
    name: 'image.jpg',
    size: 1024,
    sortOrder: 0,
    uploadStatus: 'success',
    uploadProgress: 100,
  },
]

describe('generation utilities', () => {
  it('builds a camelCase backend payload from workbench state', () => {
    const payload = buildGenerationPayload(
      'product-1',
      images,
      defaultGenerationSettings,
      productInfo,
      ['hero'],
      defaultPromptConfig,
      {
        mode: 'none',
        updateAfterGeneration: false,
      },
    )

    expect(payload).toMatchObject({
      productId: 'product-1',
      images: ['https://example.com/image.jpg'],
      platform: 'amazon',
      country: 'US',
      language: 'en',
      productInfo,
      modules: ['hero'],
      promptConfig: defaultPromptConfig,
      styleMemory: {
        mode: 'none',
        updateAfterGeneration: false,
      },
    })
  })

  it('validates the required generation draft fields', () => {
    expect(validateGenerationDraft(productInfo, images, ['hero'])).toEqual({ ok: true, messages: [] })
    expect(validateGenerationDraft({ ...productInfo, productName: '' }, [], [])).toMatchObject({ ok: false })
  })

  it('creates ordered local mock modules for offline previews', () => {
    const result = createMockResult('task-1', 'product-1', 'Test Grinder', ['hero', 'faq'])

    expect(result.taskId).toBe('task-1')
    expect(result.modules.map((module) => module.sortOrder)).toEqual([0, 1])
    expect(result.modules[0].title).toContain('Test Grinder')
  })
})
