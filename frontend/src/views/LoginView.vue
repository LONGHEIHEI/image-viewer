<template>
  <div class="login">
    <n-card class="panel card" :bordered="false">
      <div class="brand-header">
        <div class="brand-mark" aria-hidden="true">IV</div>
        <div class="brand-copy">
          <div class="brand-name">轻图</div>
          <div class="brand-subtitle">轻量图片浏览器</div>
        </div>
      </div>
      <n-form @submit.prevent="submit">
        <n-form-item label="用户名">
          <n-input
            v-model:value="username"
            placeholder="请输入用户名"
            :input-props="usernameInputProps"
            @keydown.enter.prevent="submit"
          />
        </n-form-item>
        <n-form-item label="密码">
          <n-input
            v-model:value="password"
            type="password"
            placeholder="请输入密码"
            :input-props="passwordInputProps"
            @keydown.enter.prevent="submit"
          />
        </n-form-item>
        <div :class="['actions', { 'actions--pwa': isStandalonePwa }]">
          <n-button type="primary" :block="!isStandalonePwa" :loading="auth.loading" @click="submit">登录</n-button>
        </div>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useNotification } from 'naive-ui'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const notification = useNotification()
const username = ref('')
const password = ref('')
const isStandalonePwa = ref(false)
let standaloneMedia: MediaQueryList | null = null

const usernameInputProps = {
  name: 'username',
  autocomplete: 'username',
  autocapitalize: 'none',
  autocorrect: 'off',
  spellcheck: 'false'
} as const

const passwordInputProps = {
  name: 'current-password',
  autocomplete: 'current-password',
  autocapitalize: 'none',
  autocorrect: 'off',
  spellcheck: 'false'
} as const

async function submit() {
  try {
    await auth.signIn(username.value, password.value)
    notification.success({
      title: '登录成功',
      content: `欢迎你，${auth.user?.username || username.value}`
    })
    router.push('/library')
  } catch {
    notification.error({
      title: '登录失败',
      content: auth.error || '请检查账号密码'
    })
  }
}

function updateStandaloneMode() {
  if (typeof window === 'undefined') return
  const iosStandalone = 'standalone' in window.navigator && Boolean((window.navigator as Navigator & { standalone?: boolean }).standalone)
  const mediaStandalone = standaloneMedia?.matches ?? false
  isStandalonePwa.value = iosStandalone || mediaStandalone
}

onMounted(() => {
  if (typeof window === 'undefined') return
  standaloneMedia = window.matchMedia('(display-mode: standalone), (display-mode: minimal-ui), (display-mode: fullscreen), (display-mode: window-controls-overlay)')
  updateStandaloneMode()
  if ('addEventListener' in standaloneMedia) {
    standaloneMedia.addEventListener('change', updateStandaloneMode)
  } else {
    standaloneMedia.addListener(updateStandaloneMode)
  }
})

onBeforeUnmount(() => {
  if (!standaloneMedia) return
  if ('removeEventListener' in standaloneMedia) {
    standaloneMedia.removeEventListener('change', updateStandaloneMode)
  } else {
    standaloneMedia.removeListener(updateStandaloneMode)
  }
})
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.card {
  width: min(420px, 100%);
  min-width: 320px;
  border-radius: var(--radius-lg);
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
}

.brand-mark {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: linear-gradient(140deg, var(--accent), #d4a574);
  color: #fff;
  display: grid;
  place-items: center;
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.04em;
  box-shadow: 0 14px 28px rgba(194, 101, 75, 0.24);
}

.brand-copy {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.brand-name {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.1;
  color: var(--ink);
}

.brand-subtitle {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: rgba(92, 102, 114, 0.78);
  text-transform: uppercase;
}

.actions {
  display: flex;
}

.actions--pwa {
  justify-content: flex-end;
}

@media (max-width: 640px) {
  .login {
    min-height: calc(100dvh - 40px);
    align-items: flex-start;
    padding-top: 10vh;
  }

  .card {
    min-width: 0;
  }

  .brand-header {
    margin-bottom: 16px;
  }

  .brand-mark {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    font-size: 18px;
  }

  .brand-name {
    font-size: 20px;
  }

}
</style>
