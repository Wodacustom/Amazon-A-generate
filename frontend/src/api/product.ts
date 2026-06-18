// 产品接口适配层：把旧 ProductInfo 表单结构转成新后端 products 表结构。
import { request } from './request'

import type { ProductInfo, ProductInfoRecommendationRequest, ProductInfoRecommendationResponse } from '@/types/product'

export async function createProduct(payload: ProductInfo) {
  // 旧调用方只传 ProductInfo，这里补上 MVP 后端默认平台、国家和语言。
  const { data } = await request.post('/products', toMvpProductPayload(payload))
  return data
}

export async function recommendProductInfo(payload: ProductInfoRecommendationRequest) {
  // MVP 后端暂未提供商品信息推荐接口，先返回可编辑草稿，保证主流程不中断。
  return {
    productInfo: payload.productInfo,
    sellingPoints: splitSellingPoints(payload.productInfo.coreSellingPoints),
    assumptions: [],
    source: 'mvp-local',
  } satisfies ProductInfoRecommendationResponse
}

export function toMvpProductPayload(payload: ProductInfo, options?: { platform?: string; country?: string; language?: string; fileIds?: string[] }) {
  // 后端字段使用 snake_case；高级表单字段先归入 specs，便于后续智能体读取。
  return {
    name: payload.productName || '未命名商品',
    platform: options?.platform || 'amazon',
    country: options?.country || 'US',
    language: options?.language || 'zh-CN',
    selling_points: splitSellingPoints(payload.coreSellingPoints),
    specs: {
      targetAudience: payload.targetAudience,
      useScenes: payload.useScenes,
      specifications: payload.specifications,
      brandTone: payload.brandTone,
      forbiddenWords: payload.forbiddenWords,
      complianceNotes: payload.complianceNotes,
    },
    description: payload.useScenes || payload.coreSellingPoints || null,
    file_ids: options?.fileIds || [],
  }
}

function splitSellingPoints(value: string) {
  // 兼容用户用分号、逗号、换行输入卖点。
  return value
    .split(/[;；,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean)
}
