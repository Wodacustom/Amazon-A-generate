import type { ProductImage, ProductImageType } from '@/types/product'

export function createLocalProductImage(file: File, type: ProductImageType, sortOrder: number): ProductImage {
  return {
    id: crypto.randomUUID(),
    url: URL.createObjectURL(file),
    type,
    name: file.name,
    size: file.size,
    sortOrder,
    uploadStatus: 'success',
    uploadProgress: 100,
  }
}
