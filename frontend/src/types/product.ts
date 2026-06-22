export type ProductImageType = 'main' | 'reference' | 'scene' | 'model'
export type UploadStatus = 'ready' | 'uploading' | 'success' | 'error'

export interface ProductImage {
  id: string
  url: string
  type: ProductImageType
  name: string
  size: number
  sortOrder: number
  uploadStatus: UploadStatus
  uploadProgress: number
}

export interface ProductInfo {
  productName: string
  coreSellingPoints: string
  targetAudience: string
  useScenes: string
  specifications: string
  brandTone: string
  forbiddenWords: string
  complianceNotes: string
}

export interface FileUploadResponse {
  id: string
  filename: string
  contentType: string
  url: string
  storageKey: string
  // 新后端额外返回 RustFS/S3 元数据，旧组件可忽略。
  bucket?: string
  sizeBytes?: number
}

export interface ProductInfoRecommendationRequest {
  productInfo: ProductInfo
  images: string[]
  platform: string
  country: string
  language: string
  designStyle?: string
}

export interface ProductInfoRecommendationResponse {
  productInfo: ProductInfo
  sellingPoints: string[]
  assumptions: string[]
  source: string
}
