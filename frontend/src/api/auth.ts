import { request } from './request'

import type { AuthTokenResponse, CreditAccount, CreditRedemptionCode, UserProfile } from '@/types/user'

export async function registerAccount(payload: { email: string; password: string; displayName?: string }) {
  const { data } = await request.post<AuthTokenResponse>('/auth/register', payload)
  return data
}

export async function loginAccount(payload: { email: string; password: string }) {
  const { data } = await request.post<AuthTokenResponse>('/auth/login', payload)
  return data
}

export async function getCurrentUser(accessToken: string) {
  const { data } = await request.get<UserProfile>('/auth/me', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data
}

export async function getCreditAccount(accessToken: string) {
  const { data } = await request.get<CreditAccount>('/auth/credits', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data
}

export async function redeemCreditCode(accessToken: string, code: string) {
  const { data } = await request.post<CreditAccount>(
    '/auth/credits/redeem',
    { code },
    { headers: { Authorization: `Bearer ${accessToken}` } },
  )
  return data
}

export async function adminListUsers(accessToken: string) {
  const { data } = await request.get<{ items: UserProfile[] }>('/auth/admin/users', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data.items
}

export async function adminCreateUser(
  accessToken: string,
  payload: { email: string; password: string; displayName?: string; plan: string; credits: number; role: string },
) {
  const { data } = await request.post<UserProfile>('/auth/admin/users', payload, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data
}

export async function adminAdjustCredits(
  accessToken: string,
  payload: { userId: string; amount: number; reason: string },
) {
  const { data } = await request.post<CreditAccount>('/auth/admin/credits/adjust', payload, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data
}

export async function adminListCreditCodes(accessToken: string) {
  const { data } = await request.get<{ items: CreditRedemptionCode[] }>('/auth/admin/credit-codes', {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data.items
}

export async function adminCreateCreditCodes(
  accessToken: string,
  payload: { amount: number; count: number; note?: string; expiresAt?: string },
) {
  const { data } = await request.post<{ items: CreditRedemptionCode[] }>('/auth/admin/credit-codes', payload, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  return data.items
}
