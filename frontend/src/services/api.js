import axios from 'axios'

function resolveApiBase() {
  const raw = (import.meta.env.VITE_API_URL || '/api').trim()
  return raw.replace(/\/$/, '')
}

const api = axios.create({
  baseURL: resolveApiBase(),
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject(new Error(typeof message === 'string' ? message : JSON.stringify(message)))
  },
)

export async function getHealth() {
  const { data } = await api.get('/health')
  return data
}

export default api
