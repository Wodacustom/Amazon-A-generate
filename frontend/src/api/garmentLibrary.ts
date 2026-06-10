import { request } from './request'

import type { GarmentLibraryItem } from '@/types/garmentLibrary'

export async function listGarmentLibraryItems() {
  const { data } = await request.get<{ items: GarmentLibraryItem[] }>('/garment-library/items')
  return data.items
}

export async function uploadGarmentLibraryItem(file: File, options: { name?: string; tags?: string } = {}) {
  const formData = new FormData()
  formData.append('file', file)
  if (options.name) formData.append('name', options.name)
  if (options.tags) formData.append('tags', options.tags)

  const { data } = await request.post<GarmentLibraryItem>('/garment-library/items', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteGarmentLibraryItem(itemId: string) {
  const { data } = await request.delete<{ ok: boolean }>(`/garment-library/items/${itemId}`)
  return data
}
