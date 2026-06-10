import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { getCreditAccount, getCurrentUser, loginAccount } from '@/api/auth'
import type { UserProfile } from '@/types/user'

const guestProfile: UserProfile = {
  id: 'guest',
  name: '未登录',
  displayName: '未登录',
  email: '',
  credits: 0,
  plan: 'free',
  role: 'guest',
  status: 'guest',
}

export const useUserStore = defineStore('user', () => {
  const profile = ref<UserProfile>({ ...guestProfile })
  const accessToken = ref(localStorage.getItem('accessToken') || '')
  const loading = ref(false)
  const isLoggedIn = computed(() => Boolean(accessToken.value && profile.value.id !== 'guest'))
  const isAdmin = computed(() => profile.value.role === 'admin')

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const response = await loginAccount({ email, password })
      accessToken.value = response.accessToken
      localStorage.setItem('accessToken', response.accessToken)
      localStorage.setItem('adminAccessToken', response.accessToken)
      profile.value = normalizeProfile(response.user)
      await refreshCredits()
    } finally {
      loading.value = false
    }
  }

  async function restoreSession() {
    if (!accessToken.value) return
    try {
      const user = await getCurrentUser(accessToken.value)
      profile.value = normalizeProfile(user)
      await refreshCredits()
    } catch {
      logout()
    }
  }

  async function refreshCredits() {
    if (!accessToken.value) return
    const account = await getCreditAccount(accessToken.value)
    profile.value = { ...profile.value, credits: account.balance }
  }

  function logout() {
    accessToken.value = ''
    localStorage.removeItem('accessToken')
    localStorage.removeItem('adminAccessToken')
    profile.value = { ...guestProfile }
  }

  function normalizeProfile(user: UserProfile): UserProfile {
    return {
      ...user,
      name: user.name || user.displayName || user.email,
      displayName: user.displayName || user.name || user.email,
    }
  }

  return { accessToken, profile, loading, isLoggedIn, isAdmin, login, logout, refreshCredits, restoreSession }
})
