import axios from 'axios'

const tokenKey = 'aibg_token'

export const authStore = {
  getToken: () => localStorage.getItem(tokenKey),
  setToken: (token) => localStorage.setItem(tokenKey, token),
  clearToken: () => localStorage.removeItem(tokenKey),
}

export const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = authStore.getToken()
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      authStore.clearToken()
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:expired'))
      }
    }
    return Promise.reject(error)
  },
)
