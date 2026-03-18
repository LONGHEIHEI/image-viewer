<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-notification-provider placement="top-right">
      <n-layout class="app">
        <div v-if="showMobileTopbar" :class="['app-topbar', { 'app-topbar--image': isImageRoute }]">
          <div class="topbar-left">
            <n-button
              v-if="showTopbarBackButton"
              class="menu-toggle"
              quaternary
              circle
              @click="goBack"
            >
              <template #icon>
                <svg viewBox="0 0 24 24" class="menu-toggle-icon" aria-hidden="true">
                  <path
                    d="M15 6l-6 6l6 6"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </template>
            </n-button>
            <n-button v-else class="menu-toggle" quaternary circle @click="drawerActive = true">
              <template #icon>
                <svg viewBox="0 0 24 24" class="menu-toggle-icon" aria-hidden="true">
                  <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                </svg>
              </template>
            </n-button>
            <div v-if="currentMobileTitle" class="mobile-page-heading">
              <div class="mobile-page-title">{{ currentMobileTitle }}</div>
            </div>
          </div>
          <div class="topbar-right">
            <div class="topbar-meta" v-if="showTopbarMediaCount">
              {{ topbarMediaCount }}
            </div>
            <div v-else-if="showBrandHeader" class="brand brand--topbar">
              <div class="logo">IV</div>
            </div>
          </div>
        </div>

        <n-button
          v-if="showFloatingNavButton"
          class="immersive-menu-toggle"
          quaternary
          circle
          @click="handleFloatingNav"
        >
          <template #icon>
            <svg v-if="showFloatingBackButton" viewBox="0 0 24 24" class="menu-toggle-icon" aria-hidden="true">
              <path
                d="M15 6l-6 6l6 6"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <svg v-else viewBox="0 0 24 24" class="menu-toggle-icon" aria-hidden="true">
              <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
          </template>
        </n-button>

        <div v-if="showFloatingMediaCount" class="immersive-meta-badge">
          {{ topbarMediaCount }}
        </div>

        <n-layout has-sider class="app-shell">
          <n-layout-sider v-if="showSider" class="app-sider" width="220">
            <div class="sider-inner">
              <div class="sider-brand">
                <div class="logo">IV</div>
                <div class="title">轻图</div>
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
          <n-layout-content :class="['app-content', { 'app-content--album': isAlbumBrowseRoute }]">
            <div
              :class="[
                'page-container',
                {
                  'page-container--with-topbar': showMobileTopbar,
                  'page-container--image': isImageRoute,
                  'page-container--collection': isCollectionRoute
                }
              ]"
            >
              <router-view />
            </div>
          </n-layout-content>
        </n-layout>

        <n-drawer v-model:show="drawerActive" placement="left" :width="drawerWidth">
          <n-drawer-content>
            <template #header>
              <div class="drawer-header-brand">
                <div class="logo">IV</div>
                <div class="title">轻图</div>
              </div>
            </template>
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
import { computed, h, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'
import { useGalleryStore } from './store/gallery'

const PWA_SIMULATION_KEY = 'image-views:pwa-simulated'
const PWA_QUERY_ENABLE_VALUES = new Set(['1', 'true', 'on', 'yes'])
const PWA_QUERY_DISABLE_VALUES = new Set(['0', 'false', 'off', 'no'])

const auth = useAuthStore()
const gallery = useGalleryStore()
const router = useRouter()
const route = useRoute()
const drawerActive = ref(false)
const isMobile = ref(false)
const isStandalonePwa = ref(false)
const simulatedStandalonePwa = ref(false)
let menuMedia: MediaQueryList | null = null
let standaloneMedia: MediaQueryList | null = null

const themeOverrides = {
  common: {
    primaryColor: '#ff6a3d',
    primaryColorHover: '#ff7b54',
    primaryColorPressed: '#f85b2a',
    primaryColorSuppl: '#ff6a3d',
    borderRadius: '12px',
    fontFamily: "'Archivo', Arial, sans-serif",
    fontFamilyMono: "'Space Grotesk', 'Archivo', Arial, sans-serif"
  },
  Button: {
    borderRadiusSmall: '10px',
    borderRadiusMedium: '12px',
    borderRadiusLarge: '14px'
  },
  Input: {
    borderRadius: '12px'
  },
  Card: {
    borderRadius: '16px'
  },
  Drawer: {
    color: 'rgba(255, 255, 255, 0.92)'
  },
  Layout: {
    color: 'transparent',
    siderColor: 'rgba(255, 255, 255, 0.92)'
  }
} as const

const showMenu = computed(() => {
  if (route.path === '/login') return false
  return Boolean(auth.user)
})

const isImageRoute = computed(() => route.path === '/image')
const isCollectionRoute = computed(() => route.path.startsWith('/collection/'))
const isArchiveRoute = computed(() => route.path === '/folder' && Boolean(route.query.archive))
const isAlbumBrowseRoute = computed(
  () => isCollectionRoute.value || (route.path === '/folder' && Boolean(route.query.collection))
)
const useImmersiveMobileChrome = computed(
  () => showMenu.value && isMobile.value && isStandalonePwa.value && isImageRoute.value
)
const showMobileTopbar = computed(() => showMenu.value && isMobile.value && !useImmersiveMobileChrome.value)
const showTopbarBackButton = computed(() => isImageRoute.value || isCollectionRoute.value || isArchiveRoute.value)
const showFloatingBackButton = computed(() => useImmersiveMobileChrome.value)
const showFloatingMenuButton = computed(() => false)
const showFloatingNavButton = computed(() => showFloatingBackButton.value || showFloatingMenuButton.value)
const showSider = computed(() => showMenu.value && !isMobile.value)
const drawerWidth = computed(() => (isMobile.value ? 288 : 260))
const showBrandHeader = computed(() => route.meta.topLevel !== false)
const topbarMediaCount = computed(() => {
  if (isArchiveRoute.value) {
    if (route.query.collection) {
      const total = Number(gallery.collectionArchiveListing?.total_files || 0)
      return total > 0 ? `共 ${total} 张` : ''
    }
    const total = Number(gallery.archiveListing?.total_files || 0)
    return total > 0 ? `共 ${total} 张` : ''
  }
  if (!isCollectionRoute.value) return ''
  const total = Number(gallery.collectionListing?.total_images || 0)
  return total > 0 ? `共 ${total} 张` : ''
})
const showTopbarMediaCount = computed(() => showMobileTopbar.value && Boolean(topbarMediaCount.value))
const showFloatingMediaCount = computed(
  () => useImmersiveMobileChrome.value && Boolean(topbarMediaCount.value)
)

function basename(value: string) {
  const parts = value.split(/[\\/]+/).filter(Boolean)
  return parts[parts.length - 1] || value
}

const currentMobileTitle = computed(() => {
  if (route.path === '/folder') {
    const archive = String(route.query.archive || gallery.archivePath || '')
    return archive ? basename(archive) : '内容'
  }
  if (route.path === '/image') return ''
  if (route.path.startsWith('/collection/')) return gallery.collectionName || '图集'
  if (route.path === '/settings') return '设置'
  if (route.path === '/collections') return '图集'
  return '图库'
})

function renderMenuIcon(type: 'library' | 'collections' | 'settings') {
  const paths: Record<string, string[]> = {
    library: ['M4 5h16v5H4z', 'M4 14h16v5H4z'],
    collections: ['M6 4h12v4H6z', 'M5 10h14v10H5z'],
    settings: [
      'M12 8a4 4 0 1 1 0 8a4 4 0 0 1 0-8z',
      'M3 12h2',
      'M19 12h2',
      'M12 3v2',
      'M12 19v2',
      'M5.5 5.5l1.4 1.4',
      'M17.1 17.1l1.4 1.4',
      'M5.5 18.5l1.4-1.4',
      'M17.1 6.9l1.4-1.4'
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
  const base = [{ label: '图集', key: '/collections', icon: renderMenuIcon('collections') }]
  if (auth.user?.is_admin) {
    base.push({ label: '设置', key: '/settings', icon: renderMenuIcon('settings') })
  }
  return base
})

const activeMenu = computed(() => {
  if (route.path.startsWith('/settings')) return '/settings'
  return '/collections'
})

function handleMenu(key: string) {
  router.push(key)
  drawerActive.value = false
}

function goBack() {
  router.back()
}

function handleFloatingNav() {
  if (showFloatingBackButton.value) {
    goBack()
    return
  }
  drawerActive.value = true
}

function logout() {
  auth.signOut()
  router.push('/login')
}

function updateIsMobile() {
  isMobile.value = menuMedia?.matches ?? false
}

function normalizePwaQueryValue(value: unknown) {
  const raw = Array.isArray(value) ? value[0] : value
  return typeof raw === 'string' ? raw.trim().toLowerCase() : ''
}

function readStoredPwaSimulation() {
  if (typeof window === 'undefined') return false
  return window.sessionStorage.getItem(PWA_SIMULATION_KEY) === '1'
}

function syncPwaSimulation(queryValue: unknown) {
  if (typeof window === 'undefined') return
  const normalized = normalizePwaQueryValue(queryValue)
  if (PWA_QUERY_ENABLE_VALUES.has(normalized)) {
    window.sessionStorage.setItem(PWA_SIMULATION_KEY, '1')
  } else if (PWA_QUERY_DISABLE_VALUES.has(normalized)) {
    window.sessionStorage.removeItem(PWA_SIMULATION_KEY)
  }
  simulatedStandalonePwa.value = readStoredPwaSimulation()
}

function updateStandaloneMode() {
  if (typeof window === 'undefined') return
  const iosStandalone = 'standalone' in window.navigator && Boolean((window.navigator as Navigator & { standalone?: boolean }).standalone)
  const mediaStandalone = standaloneMedia?.matches ?? false
  isStandalonePwa.value = iosStandalone || mediaStandalone || simulatedStandalonePwa.value
}

watch(
  () => route.query.pwa,
  (value) => {
    syncPwaSimulation(value)
    updateStandaloneMode()
  },
  { immediate: true }
)

onMounted(() => {
  if (typeof window === 'undefined') return
  menuMedia = window.matchMedia('(max-width: 960px)')
  standaloneMedia = window.matchMedia('(display-mode: standalone), (display-mode: minimal-ui), (display-mode: fullscreen), (display-mode: window-controls-overlay)')
  simulatedStandalonePwa.value = readStoredPwaSimulation()
  updateIsMobile()
  updateStandaloneMode()
  if ('addEventListener' in menuMedia) {
    menuMedia.addEventListener('change', updateIsMobile)
  } else {
    menuMedia.addListener(updateIsMobile)
  }
  if ('addEventListener' in standaloneMedia) {
    standaloneMedia.addEventListener('change', updateStandaloneMode)
  } else {
    standaloneMedia.addListener(updateStandaloneMode)
  }
})

onBeforeUnmount(() => {
  if (menuMedia) {
    if ('removeEventListener' in menuMedia) {
      menuMedia.removeEventListener('change', updateIsMobile)
    } else {
      menuMedia.removeListener(updateIsMobile)
    }
  }
  if (standaloneMedia) {
    if ('removeEventListener' in standaloneMedia) {
      standaloneMedia.removeEventListener('change', updateStandaloneMode)
    } else {
      standaloneMedia.removeListener(updateStandaloneMode)
    }
  }
})
</script>

<style scoped>
.app {
  min-height: 100dvh;
  background: transparent;
  --mobile-topbar-offset: calc(var(--mobile-topbar-height) + 10px + env(safe-area-inset-top));
}

.app-topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: var(--mobile-topbar-height);
  padding:
    calc(8px + env(safe-area-inset-top))
    calc(16px + env(safe-area-inset-right))
    8px
    calc(16px + env(safe-area-inset-left));
  background: var(--panel-strong);
  border-bottom: 1px solid var(--stroke);
  backdrop-filter: blur(18px);
}

.app-topbar--image {
  background: rgba(246, 246, 246, 0.82);
  backdrop-filter: blur(18px);
}

.immersive-menu-toggle {
  position: fixed;
  top: calc(12px + env(safe-area-inset-top));
  left: calc(12px + env(safe-area-inset-left));
  z-index: 30;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(27, 30, 39, 0.08);
  box-shadow: 0 10px 24px rgba(20, 25, 35, 0.14);
  backdrop-filter: blur(12px);
}

.immersive-meta-badge {
  position: fixed;
  top: calc(12px + env(safe-area-inset-top));
  right: calc(12px + env(safe-area-inset-right));
  z-index: 30;
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(27, 30, 39, 0.08);
  box-shadow: 0 10px 24px rgba(20, 25, 35, 0.14);
  color: var(--ink);
  font-size: 12px;
  font-weight: 700;
  backdrop-filter: blur(12px);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 0;
  margin-left: auto;
}

.topbar-meta {
  display: inline-flex;
  align-items: center;
  min-height: 26px;
  padding: 0 2px;
  color: rgba(92, 102, 114, 0.82);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.01em;
}

.app-shell {
  min-height: 100dvh;
}

.app-sider {
  background: var(--panel-strong);
  border-right: 1px solid var(--stroke);
}

.app-content {
  min-width: 0;
}

.page-container--with-topbar {
  padding-top: var(--mobile-topbar-offset);
}

.page-container--image {
  padding-top: 0;
}

.page-container--collection {
  padding-top: 0;
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
  min-height: calc(100dvh - 96px);
}

.drawer-header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand {
  display: flex;
  gap: 14px;
  align-items: center;
}

.brand--topbar {
  justify-content: flex-end;
}

.mobile-page-heading {
  min-width: 0;
  display: flex;
  align-items: center;
}

.mobile-page-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

@media (max-width: 960px) {
  .app-topbar {
    gap: 10px;
    padding:
      calc(6px + env(safe-area-inset-top))
      calc(14px + env(safe-area-inset-right))
      6px
      calc(14px + env(safe-area-inset-left));
  }

  .app-topbar--image {
    justify-content: flex-start;
  }

  .immersive-menu-toggle {
    top: calc(10px + env(safe-area-inset-top));
    left: calc(10px + env(safe-area-inset-left));
  }

  .immersive-meta-badge {
    top: calc(10px + env(safe-area-inset-top));
    right: calc(10px + env(safe-area-inset-right));
  }

  .topbar-left {
    min-width: 0;
  }

  .brand {
    gap: 10px;
    min-width: 0;
  }

  .mobile-page-title {
    font-size: 17px;
  }

  .title {
    font-size: 18px;
  }

  .user .name {
    font-size: 13px;
  }

  .page-container--image {
    padding:
      0 calc(10px + env(safe-area-inset-right))
      calc(var(--mobile-viewer-toolbar-space) + env(safe-area-inset-bottom))
      calc(10px + env(safe-area-inset-left));
  }

  .page-container--with-topbar.page-container--image {
    padding-top: calc(var(--mobile-topbar-height) + 6px + env(safe-area-inset-top));
  }

  .page-container--with-topbar.page-container--collection {
    padding-top: var(--mobile-topbar-offset);
  }

  .page-container--collection {
    padding-top: 0;
  }
}

@media (min-width: 961px) {
  .app-shell,
  .app-content,
  .page-container {
    min-height: 100dvh;
    width: 100%;
  }

  .app-content {
    display: flex;
    flex: 1 1 auto;
  }

  .app-content :deep(.n-layout-scroll-container) {
    display: flex;
    flex: 1 1 auto;
    width: 100%;
    min-height: 100dvh;
  }

  .page-container {
    flex: 1 1 auto;
  }
}

/* Album pages: prefer document scroll (avoid nested scrolling regions). */
.app-content--album {
  overflow: visible;
}

.app-content--album :deep(.n-layout-scroll-container) {
  overflow: visible !important;
  height: auto !important;
  min-height: 0 !important;
  display: block;
}
</style>
