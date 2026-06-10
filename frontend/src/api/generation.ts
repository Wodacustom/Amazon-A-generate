import { request } from './request'

import type { CreateGenerationTaskPayload, GenerationTask } from '@/types/generation'
import type { GenerationResult, ResultVersion } from '@/types/result'

export async function createGenerationTask(payload: CreateGenerationTaskPayload) {
  const { data } = await request.post<GenerationTask>('/generation/tasks', payload, {
    timeout: 300000,
  })
  return data
}

export async function getGenerationTask(taskId: string) {
  const { data } = await request.get<GenerationTask>(`/generation/tasks/${taskId}`)
  return data
}

export async function getGenerationResult(taskId: string) {
  const { data } = await request.get<GenerationResult>(`/generation/results/${taskId}`, {
    timeout: 60000,
  })
  return data
}

export async function updateGenerationResult(resultId: string, payload: Partial<GenerationResult> & { versionLabel?: string }) {
  const { data } = await request.put<GenerationResult>(`/generation/results/${resultId}`, payload)
  return data
}

export async function listResultVersions(resultId: string) {
  const { data } = await request.get<{ items: ResultVersion[] }>(`/generation/results/${resultId}/versions`)
  return data.items
}

export async function createResultVersion(resultId: string, label?: string) {
  const { data } = await request.post<ResultVersion>(`/generation/results/${resultId}/versions`, { label })
  return data
}

export async function restoreResultVersion(resultId: string, versionId: string) {
  const { data } = await request.post<GenerationResult>(`/generation/results/${resultId}/versions/${versionId}/restore`)
  return data
}
