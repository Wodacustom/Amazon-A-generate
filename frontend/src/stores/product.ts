import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import type { ProductImage, ProductInfo } from '@/types/product'

export const emptyProductInfo = (): ProductInfo => ({
  productName: '',
  coreSellingPoints: '',
  targetAudience: '',
  useScenes: '',
  specifications: '',
  brandTone: '',
  forbiddenWords: '',
  complianceNotes: '',
})

export const useProductStore = defineStore('product', () => {
  const productId = ref<string>()
  const productInfo = ref<ProductInfo>(emptyProductInfo())
  const images = ref<ProductImage[]>([])

  const readyImages = computed(() => images.value.filter((image) => image.uploadStatus === 'success'))

  function applyPromptDraft(prompt: string) {
    productInfo.value.coreSellingPoints = prompt
    if (!productInfo.value.productName) {
      productInfo.value.productName = prompt.split(/[，,。]/)[0]?.slice(0, 28) || '新商品'
    }
  }

  function addImages(nextImages: ProductImage[]) {
    images.value = [...images.value, ...nextImages].map((image, index) => ({ ...image, sortOrder: index }))
  }

  function removeImage(imageId: string) {
    images.value = images.value.filter((image) => image.id !== imageId)
  }

  return { productId, productInfo, images, readyImages, applyPromptDraft, addImages, removeImage }
})
