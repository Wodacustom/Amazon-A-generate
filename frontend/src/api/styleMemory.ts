import { request } from './request'

import type { StyleMemory } from '@/types/user'

export async function listStyleMemories() {
  const { data } = await request.get<{ items: StyleMemory[] }>('/style-memories')
  return data.items
}

export async function createStyleMemory(payload: Omit<StyleMemory, 'id'>) {
  const { data } = await request.post<StyleMemory>('/style-memories', payload)
  return data
}

export async function updateStyleMemory(memoryId: string, payload: Partial<StyleMemory>) {
  const { data } = await request.put<StyleMemory>(`/style-memories/${memoryId}`, payload)
  return data
}

export async function deleteStyleMemory(memoryId: string) {
  const { data } = await request.delete<{ ok: boolean }>(`/style-memories/${memoryId}`)
  return data
}
