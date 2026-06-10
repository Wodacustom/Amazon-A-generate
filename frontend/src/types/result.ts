export interface GeneratedModule {
  id: string
  type: string
  title: string
  subtitle?: string
  description?: string
  imageUrl?: string
  visualPrompt?: string
  layout: string
  sortOrder: number
}

export interface GenerationResult {
  id: string
  taskId: string
  productId: string
  modules: GeneratedModule[]
  previewUrl?: string
  exportUrls: Record<string, string> // Record<string, string> 表示一个对象，其键为字符串，值也为字符串，类似于 Map<String, String>，python中的 dict
  qualityScore: number
  metadata: Record<string, unknown> // unknown 表示未知类型，类似于 Java 中的 Object，可以是任何类型
}

export interface ResultVersion {
  id: string
  resultId: string
  version: number
  label: string
  createdAt: string
  modules: GeneratedModule[]
  previewUrl?: string
  exportUrls: Record<string, string>
  qualityScore: number
  metadata: Record<string, unknown>
}
