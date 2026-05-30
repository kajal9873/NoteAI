<template>
  <div class="auth-shell">
    <!-- Left: Brand panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-logo">
          <span class="logo-icon">✦</span>
          <span class="logo-text">NoteAI</span>
        </div>
        <h1 class="brand-headline">
          Your thoughts,<br />
          <em>amplified by AI.</em>
        </h1>
        <p class="brand-sub">
          Capture ideas, get instant summaries, and auto-organize with tags.
        </p>
        <div class="feature-pills">
          <div class="pill"><span class="pill-dot ai"></span> AI Summarization</div>
          <div class="pill"><span class="pill-dot"></span> Auto Tagging</div>
          <div class="pill"><span class="pill-dot"></span> Markdown Editor</div>
        </div>
      </div>
      <div class="brand-grid" aria-hidden="true">
        <div v-for="i in 64" :key="i" class="grid-cell" :style="{ opacity: Math.random() * 0.4 }"></div>
      </div>
    </div>

    <!-- Right: Login form -->
    <div class="form-panel">
      <div class="form-card fade-in">
        <div class="form-header">
          <h2>Welcome back</h2>
          <p>Sign in to your NoteAI account</p>
        </div>

        <form @submit.prevent="handleLogin" novalidate>
          <div class="field">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="input"
              placeholder="you@example.com"
              autocomplete="email"
              required
            />
          </div>

          <div class="field">
            <label for="password">Password</label>
            <div class="input-wrap">
              <input
                id="password"
                v-model="form.password"
                :type="showPass ? 'text' : 'password'"
                class="input"
                placeholder="••••••••"
                autocomplete="current-password"
                required
              />
              <button type="button" class="eye-btn" @click="showPass = !showPass">
                {{ showPass ? '🙈' : '👁️' }}
              </button>
            </div>
          </div>

          <p v-if="authStore.error" class="error-msg">{{ authStore.error }}</p>

          <button
            type="submit"
            class="btn btn-primary btn-lg submit-btn"
            :disabled="authStore.loading"
          >
            <div v-if="authStore.loading" class="spinner"></div>
            <span>{{ authStore.loading ? 'Signing in...' : 'Sign In' }}</span>
          </button>
        </form>

        <div class="form-footer">
          <p>Don't have an account? <RouterLink to="/register">Create one →</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showPass  = ref(false)
const form      = reactive({ email: '', password: '' })

async function handleLogin() {
  if (!form.email || !form.password) return
  try {
    await authStore.login(form.email, form.password)
  } catch {
    // error shown from store
  }
}
</script>

<style scoped>
.auth-shell {
  display: flex;
  min-height: 100vh;
}

/* ── Brand Panel ── */
.brand-panel {
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, #0e0e18 0%, #12101e 100%);
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 60px;
}

.brand-content {
  position: relative;
  z-index: 2;
  max-width: 420px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 40px;
}

.logo-icon {
  font-size: 22px;
  color: var(--accent);
  filter: drop-shadow(0 0 10px var(--accent));
}

.logo-text {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.brand-headline {
  font-family: var(--font-display);
  font-size: clamp(32px, 3.5vw, 48px);
  line-height: 1.15;
  color: var(--text-primary);
  margin-bottom: 20px;
  letter-spacing: -0.02em;
}

.brand-headline em {
  font-style: italic;
  color: var(--accent);
}

.brand-sub {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 32px;
}

.feature-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 13px;
  color: var(--text-secondary);
}

.pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
}
.pill-dot.ai { background: var(--ai); }

/* Background grid */
.brand-grid {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  grid-template-rows: repeat(8, 1fr);
  pointer-events: none;
  z-index: 1;
}
.grid-cell {
  border: 0.5px solid rgba(91,91,214,0.08);
}

/* ── Form Panel ── */
.form-panel {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--bg);
  border-left: 1px solid var(--border);
}

.form-card {
  width: 100%;
  max-width: 360px;
}

.form-header {
  margin-bottom: 32px;
}

.form-header h2 {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin-bottom: 6px;
}

.form-header p {
  font-size: 14px;
  color: var(--text-secondary);
}

.field {
  margin-bottom: 18px;
}

.field label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.input-wrap {
  position: relative;
}

.input-wrap .input {
  padding-right: 44px;
}

.eye-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.eye-btn:hover { opacity: 1; }

.error-msg {
  font-size: 13px;
  color: var(--danger);
  margin-bottom: 14px;
  padding: 10px 14px;
  background: var(--danger-soft);
  border-radius: var(--radius-sm);
  border: 1px solid rgba(224,92,92,0.2);
}

.submit-btn {
  width: 100%;
  justify-content: center;
  margin-top: 6px;
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.form-footer a {
  color: var(--accent);
  transition: opacity 0.15s;
}
.form-footer a:hover { opacity: 0.8; }

/* Mobile responsive */
@media (max-width: 768px) {
  .auth-shell { flex-direction: column; }
  .brand-panel { padding: 40px 30px; min-height: 280px; flex: none; }
  .brand-headline { font-size: 28px; }
  .form-panel { width: 100%; border-left: none; border-top: 1px solid var(--border); }
}
</style>
