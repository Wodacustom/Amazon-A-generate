import { request } from './request'

import type { MockupRecommendationRequest, MockupRecommendationResponse, MockupTemplate } from '@/types/mockup'

export async function getMockupTemplates() {
  const { data } = await request.get<MockupTemplate[]>('/mockups/templates')
  return data
}

export async function recommendMockups(payload: MockupRecommendationRequest) {
  const { data } = await request.post<MockupRecommendationResponse>('/mockups/recommend', payload)
  return data
}

export async function createMockupTemplate(payload: Omit<MockupTemplate, 'id' | 'sourceUrl'> & { sourceUrl?: string }) {
  const { data } = await request.post<MockupTemplate>('/mockups/templates', payload)
  return data
}
