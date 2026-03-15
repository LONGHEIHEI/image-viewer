<template>
  <div class="login">
    <div class="card">
      <h2>登录</h2>
      <p>请输入账号密码</p>
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" placeholder="密码" type="password" />
      <button class="primary" :disabled="auth.loading" @click="submit">登录</button>
      <div class="error" v-if="auth.error">{{ auth.error }}</div>
      <div class="hint">默认管理员：admin / admin</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const password = ref('')

async function submit() {
  try {
    await auth.signIn(username.value, password.value)
    router.push('/')
  } catch {
    // handled by store
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
  background: #fff;
  padding: 28px;
  border-radius: 18px;
  border: 1px solid var(--stroke);
  box-shadow: var(--shadow);
  min-width: 320px;
  display: grid;
  gap: 12px;
}

.card h2 {
  margin: 0;
}

.card p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--stroke);
  font-size: 14px;
}

.primary {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 10px 18px;
  cursor: pointer;
  font-weight: 600;
}

.error {
  color: #b00020;
  font-size: 12px;
}

.hint {
  font-size: 12px;
  color: var(--muted);
}
</style>
