import { request } from './request'

export async function createConversation(payload: Record<string, unknown>) {
  const { data } = await request.post('/conversations', payload)
  return data
}
