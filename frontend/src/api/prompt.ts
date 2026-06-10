import { request } from './request'

import type { PromptOptionGroup } from '@/types/generation'

export async function getPromptOptionGroups() {
  const { data } = await request.get<{ items: PromptOptionGroup[] }>('/prompt-option-groups')
  return data.items
}
