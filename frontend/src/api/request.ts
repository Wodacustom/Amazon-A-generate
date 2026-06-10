import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

export const request = axios.create({
  baseURL,
  timeout: 20000,
})

request.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)
