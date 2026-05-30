// src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// ── Request interceptor: attach access token ──
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response interceptor: handle 401 → refresh ──
api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const { data } = await axios.post('/api/auth/refresh', { refresh_token: refresh })
        localStorage.setItem('access_token', data.access_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return api(original)
      } catch {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

// ── Auth endpoints ──
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login:    (data) => api.post('/auth/login', data),
  me:       ()     => api.get('/auth/me'),
  refresh:  (rt)   => api.post('/auth/refresh', { refresh_token: rt })
}

// ── Notes endpoints ──
export const notesAPI = {
  getAll:  (params) => api.get('/notes', { params }),         // ?search=&tag=
  getOne:  (id)     => api.get(`/notes/${id}`),
  create:  (data)   => api.post('/notes', data),
  update:  (id, d)  => api.put(`/notes/${id}`, d),
  delete:  (id)     => api.delete(`/notes/${id}`),
  // AI endpoints
  summarize: (id)   => api.post(`/notes/${id}/summarize`),
  autoTag:   (id)   => api.post(`/notes/${id}/auto-tag`)
}

export default api
