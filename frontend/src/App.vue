<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN">
    <n-notification-provider placement="top-right">
      <n-layout class="app">
        <n-layout-header class="app-header">
          <div class="app-header-inner">
            <div class="header-left">
              <n-button
                v-if="showMenu && isMobile"
                class="menu-toggle"
                quaternary
                circle
                @click="drawerActive = true"
              >
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
              <n-button size="small" @click="logout">退出</n-button>
            </div>
          </div>
        </n-layout-header>
        <n-layout has-sider class="app-body">
          <n-layout-sider v-if="showSider" class="app-sider" width="200">
            <n-menu
              :options="menuOptions"
              :value="activeMenu"
              @update:value="handleMenu"
            />
          </n-layout-sider>
          <n-layout-content>
            <div class="page-container">
              <router-view />
            </div>
          </n-layout-content>
        </n-layout>
        <n-drawer v-model:show="drawerActive" placement="left" :width="240">
          <n-drawer-content title="菜单">
            <n-menu
              :options="menuOptions"
              :value="activeMenu"
              @update:value="handleMenu"
            />
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
  NLayoutHeader,
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
    base.push({ label: '集合管理', key: '/collections', icon: renderMenuIcon('collections') })
    base.push({ label: '用户管理', key: '/users', icon: renderMenuIcon('users') })
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

.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg);
  border-bottom: 1px solid var(--stroke);
}

.app-header-inner {
  max-width: none;
  margin: 0;
  width: 100%;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.app-body {
  min-height: calc(100vh - 72px);
}

.app-sider {
  background: #fff;
  border-right: 1px solid var(--stroke);
  padding: 16px 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
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

.user .name {
  font-weight: 700;
}

@media (max-width: 900px) {
  .app-header-inner {
    padding: 10px 14px;
    flex-direction: column;
    align-items: flex-start;
  }

  .user {
    align-items: flex-start;
  }

  .app-body {
    display: block;
  }

  .app-sider {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--stroke);
  }
}
</style>
