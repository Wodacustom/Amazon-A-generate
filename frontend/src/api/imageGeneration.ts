import { request } from './request'

export interface ImageGenerationPayload {
  prompt: string
  image?: File | null
  mask?: File | null
  role?: string
  modelProfileId?: number | null
  size?: string
  n?: number
  options?: Record<string, unknown>
}

export interface GeneratedImageItem {
  file_id: string
  image_url: string
  expires_in: number
  provider: string
  model: string
  operation: string
}

export interface ImageGenerationResponse {
  items: GeneratedImageItem[]
  usage: Record<string, unknown>
  metadata: Record<string, unknown>
}

export async function generateImage(payload: ImageGenerationPayload) {
  const formData = new FormData()
  formData.append('prompt', payload.prompt)
  formData.append('role', payload.role || 'image_generation')
  formData.append('size', payload.size || '1024x1024')
  formData.append('n', String(payload.n || 1))
  if (payload.modelProfileId) {
    formData.append('model_profile_id', String(payload.modelProfileId))
  }
  if (payload.image) {
    formData.append('image', payload.image)
  }
  if (payload.mask) {
    formData.append('mask', payload.mask)
  }
  if (payload.options && Object.keys(payload.options).length) {
    formData.append('options_json', JSON.stringify(payload.options))
  }
  const { data } = await request.post<ImageGenerationResponse>('/images/generate', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 600000,
  })
  return data
}
