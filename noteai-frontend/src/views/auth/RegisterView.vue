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
          Start thinking<br />
          <em>with AI.</em>
        </h1>
        <p class="brand-sub">
          Join NoteAI and turn your raw thoughts into structured, searchable, AI-enhanced notes.
        </p>
        <div class="steps">
          <div class="step"><span class="step-num">01</span><span>Write your notes freely</span></div>
          <div class="step"><span class="step-num">02</span><span>Let AI summarize & tag them</span></div>
          <div class="step"><span class="step-num">03</span><span>Search & find anything instantly</span></div>
        </div>
      </div>
      <div class="brand-grid" aria-hidden="true">
        <div v-for="i in 64" :key="i" class="grid-cell" :style="{ opacity: Math.random() * 0.4 }"></div>
      </div>
    </div>

    <!-- Right: Register form -->
    <div class="form-panel">
      <div class="form-card fade-in">
        <div class="form-header">
          <h2>Create account</h2>
          <p>Free to start — no credit card required</p>
        </div>

        <form @submit.prevent="handleRegister" novalidate>
          <div class="field">
            <label for="name">Full Name</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              class="input"
              placeholder="Arjun Sharma"
              autocomplete="name"
              required
            />
          </div>

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
                placeholder="Min. 8 characters"
                autocomplete="new-password"
                required
              />
              <button type="button" class="eye-btn" @click="showPass = !showPass">
                {{ showPass ? '🙈' : '👁️' }}
              </button>
            </div>
            <div class="strength-bar" v-if="form.password">
              <div class="strength-fill" :class="strengthClass" :style="{ width: strengthWidth }"></div>
            </div>
          </div>

          <p v-if="authStore.error" class="error-msg">{{ authStore.error }}</p>

          <button
            type="submit"
            class="btn btn-primary btn-lg submit-btn"
            :disabled="authStore.loading || !isValid"
          >
            <div v-if="authStore.loading" class="spinner"></div>
            <span>{{ authStore.loading ? 'Creating account...' : 'Create Account →' }}</span>
          </button>
        </form>

        <div class="form-footer">
          <p>Already have an account? <RouterLink to="/login">Sign in →</RouterLink></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showPass  = ref(false)
const form      = reactive({ name: '', email: '', password: '' })

const isValid = computed(() =>
  form.name.trim() && form.email.includes('@') && form.password.length >= 8
)

const strength = computed(() => {
  const p = form.password
  if (!p) return 0
  let s = 0
  if (p.length >= 8) s++
  if (/[A-Z]/.test(p)) s++
  if (/[0-9]/.test(p)) s++
  if (/[^A-Za-z0-9]/.test(p)) s++
  return s
})

const strengthWidth = computed(() => `${(strength.value / 4) * 100}%`)
const strengthClass = computed(() => (['', 'weak', 'fair', 'good', 'strong'])[strength.value])

async function handleRegister() {
  if (!isValid.value) return
  try {
    await authStore.register(form.name, form.email, form.password)
  } catch {
    // error shown from store
  }
}
</script>

<style scoped>
/* Shared with login — same shell */
.auth-shell {
  display: flex;
  min-height: 100vh;
}

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

.steps {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.step {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.step-num {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--accent);
  min-width: 24px;
}

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
}
.eye-btn:hover { opacity: 1; }

/* Password strength */
.strength-bar {
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}
.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s, background 0.3s;
}
.strength-fill.weak   { background: var(--danger); }
.strength-fill.fair   { background: var(--warning); }
.strength-fill.good   { background: #5b9bd6; }
.strength-fill.strong { background: var(--ai); }

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
}

@media (max-width: 768px) {
  .auth-shell { flex-direction: column; }
  .brand-panel { padding: 40px 30px; min-height: 260px; flex: none; }
  .brand-headline { font-size: 28px; }
  .form-panel { width: 100%; border-left: none; border-top: 1px solid var(--border); }
}
</style>
