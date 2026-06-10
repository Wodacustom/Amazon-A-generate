export type TryonJobStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled' | 'partial_success' | string

export interface CreateTryonJobPayload {
  productAssetIds: string[]
  modelAssetIds: string[]
  productImageUrls: string[]
  modelImageUrls: string[]
  prompt: string
  outputCount: number
  ratio: string
  imageModel: string
  mode: string
  asyncProcessing?: boolean
}

export interface TryonJob {
  id: string
  status: TryonJobStatus
  progress: number
  totalItems: number
  completedItems: number
  failedItems: number
  cancelledItems: number
  createdAt: string
}

export interface TryonJobItem {
  id: string
  jobId: string
  productAssetId: string
  modelAssetId: string
  status: TryonJobStatus
  progress: number
  outputImageUrl?: string
  errorMessage?: string
  prompt?: string
}
