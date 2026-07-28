<template>
  <n-config-provider :locale="zhCN" :date-locale="dateZhCN" :theme-overrides="themeOverrides">
    <n-notification-provider placement="top-right" :duration="3000">
      <n-message-provider>
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

        <div
          v-if="showPwaRefreshPrompt"
          :class="['pwa-update-toast', { 'pwa-update-toast--image': isImageRoute }]"
          role="status"
          aria-live="polite"
        >
          <div class="pwa-update-copy">
            <div class="pwa-update-title">发现新版本</div>
            <div class="pwa-update-text">有新资源可用，刷新后即可更新。</div>
          </div>
          <div class="pwa-update-actions">
            <n-button size="small" quaternary @click="dismissRefreshPrompt">稍后</n-button>
            <n-button size="small" type="primary" @click="applyUpdate">刷新</n-button>
          </div>
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
                  'page-container--image-immersive': useImmersiveMobileChrome,
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
      </n-message-provider>
    </n-notification-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import {
  NConfigProvider,
  NNotificationProvider,
  NMessageProvider,
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
import { usePwaUpdateState } from './pwa/updateState'

const PWA_SIMULATION_KEY = 'image-views:pwa-simulated'
const PWA_QUERY_ENABLE_VALUES = new Set(['1', 'true', 'on', 'yes'])
const PWA_QUERY_DISABLE_VALUES = new Set(['0', 'false', 'off', 'no'])

const auth = useAuthStore()
const gallery = useGalleryStore()
const router = useRouter()
const route = useRoute()
const { needRefresh, applyUpdate, dismissRefreshPrompt } = usePwaUpdateState()
const drawerActive = ref(false)
const isMobile = ref(false)
const isStandalonePwa = ref(false)
const actualStandalonePwa = ref(false)
const simulatedStandalonePwa = ref(false)
const autoPreviewStandalonePwa = ref(false)
let menuMedia: MediaQueryList | null = null
let standaloneMedia: MediaQueryList | null = null
let coarsePointerMedia: MediaQueryList | null = null

const themeOverrides = {
  common: {
    primaryColor: '#c2654b',
    primaryColorHover: '#d47860',
    primaryColorPressed: '#a8553f',
    primaryColorSuppl: '#c2654b',
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
const isLibrarySubfolder = computed(() => route.path === '/library' && Boolean(route.query.path))
const isAlbumBrowseRoute = computed(
  () => isCollectionRoute.value || (route.path === '/folder' && Boolean(route.query.collection))
)
// PWA 沉浸模式已弃用，保留变量避免 breaking 其他引用
// PWA 沉浸模式已弃用（浮动按钮已移除），保留变量避免 breaking
const useImmersiveMobileChrome = computed(() => false)
const showMobileTopbar = computed(() => showMenu.value && isMobile.value && !useImmersiveMobileChrome.value && !isImageRoute.value)
const showTopbarBackButton = computed(() => isCollectionRoute.value || isArchiveRoute.value || isLibrarySubfolder.value)
// ImageView 自带返回按钮，PWA 沉浸模式不需要额外浮动返回按钮
const showFloatingBackButton = computed(() => false)
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
const showPwaRefreshPrompt = computed(() => isStandalonePwa.value && needRefresh.value)

function basename(value: string) {
  const parts = value.split(/[\\/]+/).filter(Boolean)
  return parts[parts.length - 1] || value
}

const currentMobileTitle = computed(() => {
  if (route.path === '/folder') {
    const archive = String(route.query.archive || gallery.archivePath || '')
    return archive ? basename(archive) : '内容'
  }
  if (isLibrarySubfolder.value) return basename(String(route.query.path || ''))
  if (route.path === '/image') return ''
  if (route.path.startsWith('/collection/')) return gallery.collectionName || '图集'
  if (route.path === '/favorites') return '收藏'
  if (route.path === '/settings') return '设置'
  if (route.path === '/collections') return '图集'
  return '图库'
})

function renderMenuIcon(type: 'library' | 'collections' | 'favorites' | 'settings') {
  const paths: Record<string, string[]> = {
    library: ['M4 5h16v5H4z', 'M4 14h16v5H4z'],
    collections: ['M6 4h12v4H6z', 'M5 10h14v10H5z'],
    favorites: [
      'M12 3.8l2.5 5.07l5.6.81l-4.05 3.95l.96 5.57L12 16.6l-5.01 2.6l.96-5.57L3.9 9.68l5.6-.81L12 3.8z'
    ],
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
  const base = [
    { label: '图库', key: '/library', icon: renderMenuIcon('library') },
    { label: '图集', key: '/collections', icon: renderMenuIcon('collections') },
    { label: '收藏', key: '/favorites', icon: renderMenuIcon('favorites') }
  ]
  if (auth.user?.is_admin) {
    base.push({ label: '设置', key: '/settings', icon: renderMenuIcon('settings') })
  }
  return base
})

const activeMenu = computed(() => {
  if (route.path.startsWith('/settings')) return '/settings'
  if (route.path.startsWith('/favorites')) return '/favorites'
  if (route.path === '/library' || route.path === '/folder' || route.path === '/image') return '/library'
  return '/collections'
})

function handleMenu(key: string) {
  router.push(key)
  drawerActive.value = false
}

function goBack() {
  if (isLibrarySubfolder.value) {
    const currentPath = String(route.query.path || '')
    const parentPath = currentPath.split('/').slice(0, -1).join('/')
    router.push({ path: '/library', query: parentPath ? { path: parentPath } : {} })
    return
  }
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

function hasExplicitPwaPreference() {
  if (typeof window === 'undefined') return false
  const queryValue = normalizePwaQueryValue(route.query.pwa)
  if (PWA_QUERY_ENABLE_VALUES.has(queryValue) || PWA_QUERY_DISABLE_VALUES.has(queryValue)) {
    return true
  }
  return window.sessionStorage.getItem(PWA_SIMULATION_KEY) !== null
}

function isLocalPreviewHost(hostname: string) {
  return (
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '0.0.0.0' ||
    hostname === '[::1]' ||
    /^10\./.test(hostname) ||
    /^192\.168\./.test(hostname) ||
    /^172\.(1[6-9]|2\d|3[01])\./.test(hostname)
  )
}

function updateAutoPreviewStandaloneMode() {
  if (typeof window === 'undefined') return
  const localPreview = isLocalPreviewHost(window.location.hostname)
  const looksLikeMobilePreview = (menuMedia?.matches ?? false) && (coarsePointerMedia?.matches ?? false)
  autoPreviewStandalonePwa.value = localPreview && looksLikeMobilePreview && !hasExplicitPwaPreference()
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
  actualStandalonePwa.value = iosStandalone || mediaStandalone
  updateAutoPreviewStandaloneMode()
  isStandalonePwa.value =
    actualStandalonePwa.value || simulatedStandalonePwa.value || autoPreviewStandalonePwa.value
}

function syncDocumentPwaMode() {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  const body = document.body
  const isPreviewMode = !actualStandalonePwa.value && isStandalonePwa.value
  root.dataset.pwaMode = isStandalonePwa.value ? 'standalone' : 'browser'
  if (isPreviewMode) {
    root.dataset.pwaPreview = '1'
    body?.setAttribute('data-pwa-preview', '1')
  } else {
    delete root.dataset.pwaPreview
    body?.removeAttribute('data-pwa-preview')
  }
}

watch(
  () => route.query.pwa,
  (value) => {
    syncPwaSimulation(value)
    updateStandaloneMode()
  },
  { immediate: true }
)

watch([isStandalonePwa, actualStandalonePwa], () => {
  syncDocumentPwaMode()
})

watch(
  () => auth.token,
  (token) => {
    if (token) {
      gallery.loadFavorites()
      return
    }
    gallery.clearFavorites()
  },
  { immediate: true }
)

onMounted(() => {
  if (typeof window === 'undefined') return
  menuMedia = window.matchMedia('(max-width: 960px)')
  standaloneMedia = window.matchMedia('(display-mode: standalone), (display-mode: minimal-ui), (display-mode: fullscreen), (display-mode: window-controls-overlay)')
  coarsePointerMedia = window.matchMedia('(pointer: coarse), (hover: none)')
  simulatedStandalonePwa.value = readStoredPwaSimulation()
  updateIsMobile()
  updateStandaloneMode()
  syncDocumentPwaMode()
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
  if ('addEventListener' in coarsePointerMedia) {
    coarsePointerMedia.addEventListener('change', updateStandaloneMode)
  } else {
    coarsePointerMedia.addListener(updateStandaloneMode)
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
  if (coarsePointerMedia) {
    if ('removeEventListener' in coarsePointerMedia) {
      coarsePointerMedia.removeEventListener('change', updateStandaloneMode)
    } else {
      coarsePointerMedia.removeListener(updateStandaloneMode)
    }
  }
})
</script>

<style scoped>
.app {
  min-height: 100dvh;
  background: transparent;
  --mobile-topbar-offset: calc(var(--mobile-topbar-height) + 10px + var(--safe-area-top));
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
    calc(8px + var(--safe-area-top))
    calc(16px + var(--safe-area-right))
    8px
    calc(16px + var(--safe-area-left));
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
  top: calc(12px + var(--safe-area-top));
  left: calc(12px + var(--safe-area-left));
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
  top: calc(12px + var(--safe-area-top));
  right: calc(12px + var(--safe-area-right));
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

.pwa-update-toast {
  position: fixed;
  right: calc(16px + var(--safe-area-right));
  bottom: calc(16px + var(--safe-area-bottom));
  z-index: 35;
  display: grid;
  gap: 12px;
  width: min(360px, calc(100vw - 32px - var(--safe-area-left) - var(--safe-area-right)));
  padding: 14px 14px 12px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(27, 30, 39, 0.08);
  box-shadow: 0 18px 36px rgba(20, 25, 35, 0.16);
  backdrop-filter: blur(16px);
}

.pwa-update-toast--image {
  bottom: calc(var(--mobile-viewer-toolbar-space) + 14px + var(--safe-area-bottom));
}

.pwa-update-copy {
  display: grid;
  gap: 4px;
}

.pwa-update-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 14px;
  font-weight: 700;
  color: var(--ink);
}

.pwa-update-text {
  font-size: 12px;
  line-height: 1.45;
  color: rgba(92, 102, 114, 0.88);
}

.pwa-update-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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
  background: linear-gradient(140deg, var(--accent), #d4a574);
  color: #fff;
  font-weight: 700;
  font-family: 'Space Grotesk', Arial, sans-serif;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 20px rgba(194, 101, 75, 0.28);
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
      calc(6px + var(--safe-area-top))
      calc(14px + var(--safe-area-right))
      6px
      calc(14px + var(--safe-area-left));
  }

  .app-topbar--image {
    justify-content: flex-start;
  }

  .immersive-menu-toggle {
    top: calc(10px + var(--safe-area-top));
    left: calc(10px + var(--safe-area-left));
  }

  .immersive-meta-badge {
    top: calc(10px + var(--safe-area-top));
    right: calc(10px + var(--safe-area-right));
  }

  .pwa-update-toast {
    left: calc(10px + var(--safe-area-left));
    right: calc(10px + var(--safe-area-right));
    bottom: calc(12px + var(--safe-area-bottom));
    width: auto;
    gap: 10px;
    padding: 12px;
    border-radius: 16px;
  }

  .pwa-update-toast--image {
    bottom: calc(var(--mobile-viewer-toolbar-space) + 12px + var(--safe-area-bottom));
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

  .pwa-update-actions {
    width: 100%;
  }

  .page-container--image {
    padding:
      0 calc(10px + var(--safe-area-right))
      calc(var(--mobile-viewer-toolbar-space) + var(--safe-area-bottom))
      calc(10px + var(--safe-area-left));
  }

  .page-container--image.page-container--image-immersive {
    padding-top: calc(var(--mobile-viewer-top-chrome-space) + var(--safe-area-top));
  }

  .page-container--with-topbar.page-container--image {
    padding-top: calc(var(--mobile-topbar-height) + 6px + var(--safe-area-top));
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
