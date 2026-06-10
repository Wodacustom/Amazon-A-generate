import type { ProductImage, ProductInfo } from '@/types/product'

export interface ValidationResult {
  ok: boolean
  messages: string[]
}

export function validateGenerationDraft(productInfo: ProductInfo, images: ProductImage[], modules: string[]): ValidationResult {
  const messages: string[] = []

  if (!productInfo.productName.trim()) {
    messages.push('请填写商品名称')
  }
  if (!productInfo.coreSellingPoints.trim()) {
    messages.push('请填写核心卖点')
  }
  if (!images.some((image) => image.uploadStatus === 'success')) {
    messages.push('请上传至少一张商品图或参考图')
  }
  if (modules.length === 0) {
    messages.push('请选择至少一个详情页模块')
  }

  return { ok: messages.length === 0, messages }
}
