<template>
  <div class="app">
    <header class="hero">
      <div class="hero-inner">
        <div class="brand">
          <div class="logo">IV</div>
          <div>
            <div class="title">写真浏览器</div>
            <div class="subtitle">文件夹优先 · 支持压缩包直读</div>
          </div>
        </div>
        <div class="badges">
          <span>PWA</span>
          <span>ZIP / 7Z / RAR</span>
          <span>Docker</span>
        </div>
        <div class="user" v-if="auth.user">
          <div class="name">{{ auth.user.username }}</div>
          <div class="actions">
            <button class="ghost" v-if="auth.user.is_admin" @click="goUsers">用户管理</button>
            <button class="ghost" @click="logout">退出</button>
          </div>
        </div>
      </div>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.signOut()
  router.push('/login')
}

function goUsers() {
  router.push('/users')
}
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.hero {
  padding: 28px 24px 22px;
}

.hero-inner {
  background: var(--panel);
  border: 1px solid var(--stroke);
  border-radius: 20px;
  padding: 22px;
  box-shadow: var(--shadow);
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 16px;
  align-items: center;
}

.brand {
  display: flex;
  gap: 16px;
  align-items: center;
}

.logo {
  height: 48px;
  width: 48px;
  border-radius: 14px;
  background: linear-gradient(140deg, var(--accent), #ffb84a);
  color: #fff;
  font-weight: 700;
  font-family: 'Space Grotesk', Arial, sans-serif;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 20px rgba(255, 106, 61, 0.4);
}

.title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 26px;
  font-weight: 700;
}

.subtitle {
  margin-top: 6px;
  font-size: 14px;
  color: var(--muted);
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.badges span {
  background: rgba(47, 143, 124, 0.12);
  color: var(--accent-2);
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.user {
  display: grid;
  gap: 8px;
  justify-items: end;
}

.user .name {
  font-weight: 700;
}

.actions {
  display: flex;
  gap: 8px;
}

.ghost {
  background: transparent;
  border: 1px solid var(--stroke);
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
}

.content {
  padding: 8px 24px 32px;
}

@media (max-width: 900px) {
  .hero-inner {
    grid-template-columns: 1fr;
    justify-items: start;
  }

  .user {
    justify-items: start;
  }
}
</style>
