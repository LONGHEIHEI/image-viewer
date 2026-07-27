<template>
  <div class="login">
    <div class="login-card">
      <div class="login-brand">
        <div class="login-mark">IV</div>
        <h1 class="login-title">轻图</h1>
        <p class="login-desc">登录以继续浏览</p>
      </div>

      <form class="login-form" autocomplete="on" @submit.prevent="handleSubmit">
        <div class="field">
          <input
            ref="usernameRef"
            v-model="username"
            class="input"
            type="text"
            name="username"
            autocomplete="username"
            placeholder="用户名"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            @keydown.enter="handleSubmit"
          />
        </div>
        <div class="field">
          <input
            v-model="password"
            class="input"
            type="password"
            name="password"
            autocomplete="current-password"
            placeholder="密码"
            autocapitalize="none"
            autocorrect="off"
            spellcheck="false"
            @keydown.enter="handleSubmit"
          />
        </div>
        <button
          type="submit"
          class="submit-btn"
          :disabled="auth.loading"
        >
          <span v-if="auth.loading" class="spinner"></span>
          <span>{{ auth.loading ? '登录中...' : '登 录' }}</span>
        </button>
      </form>

      <p v-if="auth.error" class="login-error">{{ auth.error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotification } from 'naive-ui'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const notification = useNotification()

const username = ref('')
const password = ref('')
const usernameRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  usernameRef.value?.focus()
})

async function handleSubmit() {
  if (!username.value || !password.value) return
  try {
    await auth.signIn(username.value, password.value)
    notification.success({
      title: '登录成功',
      content: `欢迎回来，${auth.user?.username || username.value}`
    })
    router.push('/library')
  } catch {
    // error set by store
  }
}
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100dvh;
  padding: 24px;
  background:
    radial-gradient(ellipse 70% 50% at 50% 40%, rgba(194, 101, 75, 0.04), transparent),
    linear-gradient(180deg, var(--bg) 0%, #ece8e2 100%);
}

.login-card {
  width: min(380px, 100%);
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.login-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.login-mark {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: linear-gradient(145deg, var(--accent), #d4a574);
  color: #fff;
  display: grid;
  place-items: center;
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 24px;
  font-weight: 700;
  box-shadow: 0 16px 32px rgba(194, 101, 75, 0.18);
}

.login-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 28px;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  line-height: 1;
}

.login-desc {
  margin: 0;
  font-size: 14px;
  color: var(--muted);
  font-weight: 500;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field {
  position: relative;
}

.input {
  width: 100%;
  height: 50px;
  padding: 0 16px;
  border: 1px solid rgba(26, 26, 26, 0.10);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--ink);
  font-family: 'Archivo', Arial, sans-serif;
  font-size: 15px;
  font-weight: 500;
  outline: none;
  transition:
    border-color 0.18s,
    box-shadow 0.18s,
    background 0.18s;
  -webkit-appearance: none;
  appearance: none;
}

.input::placeholder {
  color: rgba(102, 100, 96, 0.45);
  font-weight: 400;
}

.input:hover {
  border-color: rgba(26, 26, 26, 0.16);
  background: rgba(255, 255, 255, 0.88);
}

.input:focus {
  border-color: rgba(194, 101, 75, 0.40);
  background: #fff;
  box-shadow: 0 0 0 4px rgba(194, 101, 75, 0.08);
}

.submit-btn {
  width: 100%;
  height: 50px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 24px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(145deg, var(--accent), #d47860);
  color: #fff;
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.12s, box-shadow 0.15s;
  box-shadow: 0 10px 24px rgba(194, 101, 75, 0.22);
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.94;
  transform: translateY(-1px);
  box-shadow: 0 14px 30px rgba(194, 101, 75, 0.26);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 6px 16px rgba(194, 101, 75, 0.18);
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 6px 16px rgba(194, 101, 75, 0.14);
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-error {
  text-align: center;
  font-size: 13px;
  color: #b00020;
  margin: 0;
  padding: 10px 16px;
  border-radius: 10px;
  background: rgba(176, 0, 32, 0.06);
}

@media (max-width: 640px) {
  .login {
    padding: 20px;
    align-items: flex-start;
    padding-top: 14vh;
  }

  .login-card {
    gap: 28px;
  }

  .login-mark {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    font-size: 21px;
  }

  .login-title {
    font-size: 26px;
  }

  .input {
    height: 48px;
    font-size: 16px; /* prevents iOS zoom */
  }

  .submit-btn {
    height: 48px;
  }
}
</style>
