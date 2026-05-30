// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user        = ref(null)
  const loading     = ref(false)
  const error       = ref(null)

  const isLoggedIn  = computed(() => !!user.value)
  const initials    = computed(() => {
    if (!user.value?.name) return '?'
    return user.value.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  })

  // ── Init: restore session ──
  async function init() {
    const token = localStorage.getItem('access_token')
    if (!token) return
    try {
      const { data } = await authAPI.me()
      user.value = data
    } catch {
      logout()
    }
  }

  // ── Register ──
  async function register(name, email, password) {
    loading.value = true
    error.value   = null
    try {
      await authAPI.register({ name, email, password })
      await login(email, password)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // ── Login ──
  async function login(email, password) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await authAPI.login({ email, password })
      localStorage.setItem('access_token',  data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      user.value = data.user
      router.push('/dashboard')
    } catch (err) {
      error.value = err.response?.data?.detail || 'Invalid credentials'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // ── Logout ──
  function logout() {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  }

  return { user, loading, error, isLoggedIn, initials, init, register, login, logout }
})
