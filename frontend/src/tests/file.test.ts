import { describe, expect, it, vi } from 'vitest'

import { createLocalProductImage } from '@/utils/file'

describe('createLocalProductImage', () => {
  it('creates a local image record for immediate preview', () => {
    vi.stubGlobal('crypto', { randomUUID: () => 'image-1' })
    vi.stubGlobal('URL', { createObjectURL: () => 'blob:preview' })

    const image = createLocalProductImage(new File(['image'], 'product.png', { type: 'image/png' }), 'main', 0)

    expect(image).toMatchObject({
      id: 'image-1',
      url: 'blob:preview',
      type: 'main',
      name: 'product.png',
      sortOrder: 0,
      uploadStatus: 'success',
    })
  })
})
