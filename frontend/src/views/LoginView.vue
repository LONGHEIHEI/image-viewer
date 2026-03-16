<template>
  <div class="login">
    <n-card class="panel card" title="登录" :bordered="false">
      <n-form>
        <n-form-item label="用户名">
          <n-input v-model:value="username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="password" type="password" placeholder="请输入密码" />
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

async function submit() {
  try {
    await auth.signIn(username.value, password.value)
    notification.success({
      title: '登录成功',
      content: `欢迎你，${auth.user?.username || username.value}`
    })
    router.push('/collections')
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
}
</style>
