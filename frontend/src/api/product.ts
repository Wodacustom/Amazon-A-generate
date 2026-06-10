import { request } from './request'

import type { ProductInfo, ProductInfoRecommendationRequest, ProductInfoRecommendationResponse } from '@/types/product'

export async function createProduct(payload: ProductInfo) {
  const { data } = await request.post('/products', payload)
  return data
}

export async function recommendProductInfo(payload: ProductInfoRecommendationRequest) {
  const { data } = await request.post<ProductInfoRecommendationResponse>('/products/recommend-info', payload, {
    timeout: 120000,
  })
  return data
}
