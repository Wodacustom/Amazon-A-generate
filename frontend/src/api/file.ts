import { request } from './request'

import type { FileUploadResponse } from '@/types/product'

export async function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  const { data } = await request.post<FileUploadResponse>('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function deleteFile(fileId: string) {
  const { data } = await request.delete<{ ok: boolean }>(`/files/${fileId}`)
  return data
}
