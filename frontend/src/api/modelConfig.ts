import { request } from './request'

export type ModelType = 'chat' | 'embedding' | 'image'
export type ModelProvider = 'mock' | 'openai' | 'qwen' | 'gemini' | 'vllm' | 'newapi'

export interface ModelProfile {
  id: number
  name: string
  model_type: ModelType
  provider: ModelProvider
  model: string
  base_url: string | null
  api_key_configured: boolean
  masked_api_key: string | null
  timeout_seconds: number
  temperature: number | null
  dimensions: number | null
  config: Record<string, unknown>
  enabled: boolean
}

export interface ModelProfilePayload {
  name?: string
  model_type?: ModelType
  provider?: ModelProvider
  model?: string
  base_url?: string | null
  api_key?: string | null
  timeout_seconds?: number
  temperature?: number | null
  dimensions?: number | null
  config?: Record<string, unknown>
  enabled?: boolean
}

export async function listModelProfiles() {
  const { data } = await request.get<{ items: ModelProfile[] }>('/admin/model-config/profiles')
  return data.items
}

export async function createModelProfile(payload: ModelProfilePayload) {
  const { data } = await request.post<ModelProfile>('/admin/model-config/profiles', payload)
  return data
}

export async function updateModelProfile(profileId: number, payload: ModelProfilePayload) {
  const { data } = await request.patch<ModelProfile>(`/admin/model-config/profiles/${profileId}`, payload)
  return data
}

export async function deleteModelProfile(profileId: number) {
  const { data } = await request.delete<{ ok: boolean }>(`/admin/model-config/profiles/${profileId}`)
  return data
}
