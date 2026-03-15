<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-notification-provider placement="top-right">
      <n-layout class="app">
        <div v-if="showMenu && isMobile" class="app-topbar">
          <div class="topbar-left">
            <n-button class="menu-toggle" quaternary circle @click="drawerActive = true">
              <template #icon>
                <svg viewBox="0 0 24 24" class="menu-toggle-icon" aria-hidden="true">
                  <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </template>
            </n-button>
            <div class="brand">
              <div class="logo">IV</div>
              <div class="title">写真浏览器</div>
            </div>
          </div>
          <div class="user" v-if="auth.user">
            <div class="name">{{ auth.user.username }}</div>
          </div>
        </div>

        <n-layout has-sider class="app-shell">
          <n-layout-sider v-if="showSider" class="app-sider" width="220">
            <div class="sider-inner">
              <div class="sider-brand">
                <div class="logo">IV</div>
                <div class="title">写真浏览器</div>
              </div>
              <n-menu
                class="sider-menu"
                :options="menuOptions"
                :value="activeMenu"
                @update:value="handleMenu"
              />
              <div class="sider-user" v-if="auth.user">
                <div class="name">{{ auth.user.username }}</div>
                <n-button size="small" @click="logout">退出登录</n-button>
              </div>
            </div>
          </n-layout-sider>
          <n-layout-content class="app-content">
            <div class="page-container">
              <router-view />
            </div>
          </n-layout-content>
        </n-layout>

        <n-drawer v-model:show="drawerActive" placement="left" :width="260">
          <n-drawer-content title="菜单">
            <div class="drawer-inner">
              <n-menu
                :options="menuOptions"
                :value="activeMenu"
                @update:value="handleMenu"
              />
              <div class="sider-user" v-if="auth.user">
                <div class="name">{{ auth.user.username }}</div>
                <n-button size="small" @click="logout">退出登录</n-button>
              </div>
            </div>
          </n-drawer-content>
        </n-drawer>
      </n-layout>
    </n-notification-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import {
  NConfigProvider,
  NNotificationProvider,
  NLayout,
  NLayoutSider,
  NLayoutContent,
  NMenu,
  NButton,
  NDrawer,
  NDrawerContent,
  NIcon,
  zhCN,
  dateZhCN
} from 'naive-ui'
import { computed, h, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const drawerActive = ref(false)
const isMobile = ref(false)
let menuMedia: MediaQueryList | null = null

const showMenu = computed(() => {
  if (route.path === '/login') return false
  return Boolean(auth.user)
})

const showSider = computed(() => showMenu.value && !isMobile.value)

function renderMenuIcon(type: 'library' | 'collections' | 'users') {
  const paths: Record<string, string[]> = {
    library: ['M4 5h16v5H4z', 'M4 14h16v5H4z'],
    collections: ['M6 4h12v4H6z', 'M5 10h14v10H5z'],
    users: [
      'M12 6a3.5 3.5 0 1 1 0 7 3.5 3.5 0 0 1 0-7z',
      'M5 19v-1a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v1'
    ]
  }
  const segments = paths[type]
  return () =>
    h(
      NIcon,
      { size: 18 },
      {
        default: () =>
          h(
            'svg',
            {
              viewBox: '0 0 24 24',
              fill: 'none',
              xmlns: 'http://www.w3.org/2000/svg',
              class: 'menu-icon'
            },
            segments.map((d) =>
              h('path', {
                d,
                stroke: 'currentColor',
                'stroke-width': 1.8,
                'stroke-linecap': 'round',
                'stroke-linejoin': 'round'
              })
            )
          )
      }
    )
}

const menuOptions = computed(() => {
  const base = [{ label: '图库', key: '/', icon: renderMenuIcon('library') }]
  if (auth.user?.is_admin) {
    base.push({ label: '集合', key: '/collections', icon: renderMenuIcon('collections') })
    base.push({ label: '用户', key: '/users', icon: renderMenuIcon('users') })
  }
  return base
})

const activeMenu = computed(() => {
  if (route.path.startsWith('/collections')) return '/collections'
  if (route.path.startsWith('/users')) return '/users'
  return '/'
})

function handleMenu(key: string) {
  router.push(key)
  drawerActive.value = false
}

function logout() {
  auth.signOut()
  router.push('/login')
}

function updateIsMobile() {
  isMobile.value = menuMedia?.matches ?? false
}

onMounted(() => {
  if (typeof window === 'undefined') return
  menuMedia = window.matchMedia('(max-width: 960px)')
  updateIsMobile()
  if ('addEventListener' in menuMedia) {
    menuMedia.addEventListener('change', updateIsMobile)
  } else {
    menuMedia.addListener(updateIsMobile)
  }
})

onBeforeUnmount(() => {
  if (!menuMedia) return
  if ('removeEventListener' in menuMedia) {
    menuMedia.removeEventListener('change', updateIsMobile)
  } else {
    menuMedia.removeListener(updateIsMobile)
  }
})
</script>

<style scoped>
.app {
  min-height: 100vh;
}

.app-topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--bg);
  border-bottom: 1px solid var(--stroke);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-shell {
  height: 100vh;
}

.app-sider {
  background: #fff;
  border-right: 1px solid var(--stroke);
}

.sider-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px 12px 16px;
  gap: 12px;
}

.sider-menu :deep(.n-menu-item-content) {
  padding-left: 20px;
}

.sider-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 10px;
}

.sider-menu {
  flex: 1;
}

.sider-user {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 10px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px dashed var(--stroke);
}

.app-sider :deep(.n-layout-sider-scroll-container) {
  height: 100%;
}

.drawer-inner {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
}

.menu-toggle {
  border-radius: 12px;
}

.menu-toggle-icon {
  width: 20px;
  height: 20px;
}

.logo {
  height: 36px;
  width: 36px;
  border-radius: var(--radius-md);
  background: linear-gradient(140deg, var(--accent), #ffb84a);
  color: #fff;
  font-weight: 700;
  font-family: 'Space Grotesk', Arial, sans-serif;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 20px rgba(255, 106, 61, 0.35);
}

.title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 20px;
  font-weight: 700;
}

.user {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.user .name,
.sider-user .name {
  font-weight: 700;
}
</style>
