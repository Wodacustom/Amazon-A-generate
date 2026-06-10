export interface UserProfile {
  id: string
  name?: string
  displayName?: string
  email: string
  credits: number
  plan: string
  role?: string
  status?: string
  avatarUrl?: string
}

export interface AuthTokenResponse {
  accessToken: string
  tokenType: string
  user: UserProfile
}

export interface CreditTransaction {
  id: string
  amount: number
  balanceAfter: number
  transactionType: string
  reason: string
  relatedEntityType?: string
  relatedEntityId?: string
  createdAt: string
}

export interface CreditAccount {
  balance: number
  lifetimeEarned: number
  lifetimeSpent: number
  transactions: CreditTransaction[]
}

export interface CreditRedemptionCode {
  id: string
  code: string
  amount: number
  status: string
  note?: string
  createdByUserId?: string
  redeemedByUserId?: string
  redeemedAt?: string
  expiresAt?: string
  createdAt?: string
}

export interface StyleMemory {
  id: string
  name: string
  scope: 'user' | 'company' | 'brand'
  colors: string[]
  copyTone: string
  composition: string
  forbiddenElements: string[]
  isActive: boolean
  createdAt?: string
  updatedAt?: string
  usageCount?: number
}
