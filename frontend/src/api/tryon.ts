import { request } from './request'

import type { CreateTryonJobPayload, TryonJob, TryonJobItem } from '@/types/task'

export async function createTryonJob(payload: CreateTryonJobPayload) {
  const { data } = await request.post<TryonJob>('/tryon/jobs', payload, {
    timeout: 600000,
  })
  return data
}

export async function listTryonJobs() {
  const { data } = await request.get<{ items: TryonJob[] }>('/tryon/jobs')
  return data.items
}

export async function getTryonJob(jobId: string) {
  const { data } = await request.get<TryonJob>(`/tryon/jobs/${jobId}`)
  return data
}

export async function listTryonJobItems(jobId: string) {
  const { data } = await request.get<{ items: TryonJobItem[] }>(`/tryon/jobs/${jobId}/items`)
  return data.items
}

export async function cancelTryonJob(jobId: string) {
  const { data } = await request.post<TryonJob>(`/tryon/jobs/${jobId}/cancel`)
  return data
}
