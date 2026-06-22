import { request } from './request'

export type ModelType = 'chat' | 'embedding'
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

function authHeaders(accessToken: string) {
  return { Authorization: `Bearer ${accessToken}` }
}

export async function listModelProfiles(accessToken: string) {
  const { data } = await request.get<{ items: ModelProfile[] }>('/admin/model-config/profiles', {
    headers: authHeaders(accessToken),
  })
  return data.items
}

export async function createModelProfile(accessToken: string, payload: ModelProfilePayload) {
  const { data } = await request.post<ModelProfile>('/admin/model-config/profiles', payload, {
    headers: authHeaders(accessToken),
  })
  return data
}

export async function updateModelProfile(accessToken: string, profileId: number, payload: ModelProfilePayload) {
  const { data } = await request.patch<ModelProfile>(`/admin/model-config/profiles/${profileId}`, payload, {
    headers: authHeaders(accessToken),
  })
  return data
}

export async function deleteModelProfile(accessToken: string, profileId: number) {
  const { data } = await request.delete<{ ok: boolean }>(`/admin/model-config/profiles/${profileId}`, {
    headers: authHeaders(accessToken),
  })
  return data
}
