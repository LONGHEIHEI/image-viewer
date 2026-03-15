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
        <n-button type="primary" block :loading="auth.loading" @click="submit">登录</n-button>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useNotification } from 'naive-ui'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const notification = useNotification()
const username = ref('')
const password = ref('')

async function submit() {
  try {
    await auth.signIn(username.value, password.value)
    notification.success({
      title: '登录成功',
      content: `欢迎你，${auth.user?.username || username.value}`
    })
    router.push('/')
  } catch {
    notification.error({
      title: '登录失败',
      content: auth.error || '请检查账号密码'
    })
  }
}
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.card {
  min-width: 320px;
  border-radius: var(--radius-lg);
}
</style>
