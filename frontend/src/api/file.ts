// 文件接口适配层：旧前端仍使用 uploadFile，内部调用新后端 POST /files。
import { request } from './request'

import type { FileUploadResponse } from '@/types/product'

export async function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  // 新后端返回 snake_case 对象存储元数据。
  const { data } = await request.post<{
    id: string
    object_key: string
    bucket: string
    original_filename: string | null
    content_type: string | null
    size_bytes: number
    url: string
  }>('/files', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  // 映射回旧组件使用的 camelCase 字段，减少页面改动。
  return {
    id: data.id,
    filename: data.original_filename || file.name,
    contentType: data.content_type || file.type,
    url: data.url,
    storageKey: data.object_key,
    bucket: data.bucket,
    sizeBytes: data.size_bytes,
  } satisfies FileUploadResponse
}

export async function deleteFile(fileId: string) {
  // MVP 后端暂未提供删除对象接口，前端先只移除本地列表项。
  void fileId
  return { ok: true }
}
