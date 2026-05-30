<template>
  <RouterView />

  <!-- Global Toast Notifications -->
  <div class="toast-container">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      :class="['toast', `toast-${toast.type}`]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'

// ── Global Toast System ──
const toasts = ref([])

function showToast(message, type = 'info', duration = 3000) {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

// Provide toast globally so any component can use it
provide('toast', showToast)
</script>
