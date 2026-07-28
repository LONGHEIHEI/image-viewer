<template>
<div class="page image-page">
  <div class="top-title">{{ name }}</div>

   <div class="viewer-wrap">
     <ImageViewer
       ref="viewerRef"
       :src="src"
       :name="name"
       @scale-change="scale = $event"
       @fullscreen-change="isFullscreen = $event"
     />
   </div>

  <div class="bottom-bar">
    <div class="bb-left">
      <button class="v-btn" @click="goBack" aria-label="返回">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M18 6L6 18"/>
          <path d="M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <div class="bb-divider"></div>

    <div class="bb-center">
      <button class="v-btn v-btn--nav" :class="{ 'v-btn--off': !hasPrev }" :disabled="!hasPrev" @click="goPrev" aria-label="上一张">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
      </button>

      <span v-if="showPositionBadge" class="bb-pos">
        <span class="v-pos-curr">{{ currentPosition }}</span>
        <span class="v-pos-div">/</span>
        <span class="v-pos-total">{{ totalCount }}</span>
      </span>
      <span v-else class="bb-pos bb-pos--empty"></span>

      <button class="v-btn v-btn--nav" :class="{ 'v-btn--off': !hasNext }" :disabled="!hasNext" @click="goNext" aria-label="下一张">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
      </button>
    </div>

    <div class="bb-divider"></div>

    <div class="bb-right">
      <button class="v-btn" :class="{ 'v-btn--on': isCurrentFavorite }" @click="toggleFavorite" aria-label="收藏">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/>
        </svg>
      </button>

      <button class="v-btn" @click="infoVisible = true" aria-label="信息">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 16v-4"/>
          <path d="M12 8h.01"/>
        </svg>
      </button>

      <button class="v-btn" @click="toggleFullscreen" aria-label="全屏">
        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M15 3h6v6"/>
          <path d="M9 21H3v-6"/>
          <path d="M21 3l-7 7"/>
          <path d="M3 21l7-7"/>
        </svg>
      </button>
    </div>
  </div>

   <!-- Desktop: side drawer -->
    <n-drawer v-if="!isMobile" v-model:show="infoVisible" placement="right" :width="420">
      <n-drawer-content title="图片信息">
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">文件名</span>
            <span class="info-value">{{ name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">来源</span>
            <span class="info-value">{{ sourceLabel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">图片路径</span>
            <span class="info-value">{{ displayPath }}</span>
          </div>
          <div v-if="archive" class="info-item">
            <span class="info-label">压缩包</span>
            <span class="info-value">{{ archive }}</span>
          </div>
          <div v-if="folder" class="info-item">
            <span class="info-label">所在目录</span>
            <span class="info-value">{{ folder }}</span>
          </div>
          <div v-if="collectionId !== null" class="info-item">
            <span class="info-label">图集</span>
            <span class="info-value">{{ store.collectionName || `图集 #${collectionId}` }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">浏览模式</span>
            <span class="info-value">{{ viewMode === 'flat' ? '平铺聚合' : '文件夹' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">尺寸</span>
            <span class="info-value">{{ imageSizeText }}</span>
          </div>
        </div>
      </n-drawer-content>
    </n-drawer>

    <!-- Mobile: modal card -->
    <n-modal v-else v-model:show="infoVisible" :style="{ maxWidth: '360px' }">
      <n-card title="图片信息" closable @close="infoVisible = false">
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">文件名</span>
            <span class="info-value">{{ name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">来源</span>
            <span class="info-value">{{ sourceLabel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">图片路径</span>
            <span class="info-value">{{ displayPath }}</span>
          </div>
          <div v-if="archive" class="info-item">
            <span class="info-label">压缩包</span>
            <span class="info-value">{{ archive }}</span>
          </div>
          <div v-if="folder" class="info-item">
            <span class="info-label">所在目录</span>
            <span class="info-value">{{ folder }}</span>
          </div>
          <div v-if="collectionId !== null" class="info-item">
            <span class="info-label">图集</span>
            <span class="info-value">{{ store.collectionName || `图集 #${collectionId}` }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">浏览模式</span>
            <span class="info-value">{{ viewMode === 'flat' ? '平铺聚合' : '文件夹' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">尺寸</span>
            <span class="info-value">{{ imageSizeText }}</span>
          </div>
        </div>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NDrawer, NDrawerContent, NModal, NCard } from 'naive-ui'
import {
  archiveImageUrl,
  collectionArchiveImageUrl,
  collectionImageUrl,
  imageUrl,
  type FolderItem
} from '../api/client'
import ImageViewer from '../components/ImageViewer.vue'
import { useGalleryStore } from '../store/gallery'
import { buildFavoriteKey, favoritePayloadFromRoute, favoriteSourceLabel } from '../utils/favorites'
import {
  buildImageRouteQuery,
  getPathBasename,
  getParentFolderFromPath,
  parseCollectionId,
  parseGalleryView,
  readQueryString
} from '../utils/galleryRoute'

type ViewerExpose = {
  toggleFullscreen: () => void
  resetView: () => void
}

type SizedFolderItem = FolderItem & {
  width?: number
  height?: number
}

const viewerRef = ref<ViewerExpose | null>(null)
const scale = ref(1)
const isFullscreen = ref(false)
const infoVisible = ref(false)

const route = useRoute()
const router = useRouter()
const store = useGalleryStore()

const path = computed(() => readQueryString(route.query.path))
const archive = computed(() => readQueryString(route.query.archive))
const file = computed(() => readQueryString(route.query.file))
const folder = computed(() => readQueryString(route.query.folder))
const privacy = computed(() => route.query.privacy === '1')
const hasIndex = computed(() => route.query.index !== undefined)
const indexParam = computed(() => (hasIndex.value ? Number(route.query.index) : -1))

const collectionId = computed(() => parseCollectionId(route.query.collection))
const viewMode = computed(() => parseGalleryView(route.query.view))
const isCollection = computed(() => collectionId.value !== null)
const isMobile = computed(() => typeof window !== 'undefined' && window.innerWidth <= 960)

const src = computed(() => {
  if (archive.value && file.value) {
    if (isCollection.value) return collectionArchiveImageUrl(collectionId.value as number, archive.value, file.value)
    return archiveImageUrl(archive.value, file.value)
  }
  if (isCollection.value) return collectionImageUrl(collectionId.value as number, path.value)
  return imageUrl(path.value)
})

const name = computed(() => file.value || getPathBasename(path.value))

const items = computed(() => {
  if (isCollection.value) {
    if (archive.value && store.collectionArchiveListing?.archive === archive.value) return store.collectionArchiveListing.files
    if (!archive.value && store.collectionListing?.folder === (folder.value || store.collectionFolder)) return store.collectionListing.images
    return []
  }
  if (archive.value && store.archiveListing?.archive === archive.value) return store.archiveListing.files
  if (!archive.value && store.listing?.folder === (folder.value || store.currentFolder)) return store.listing.images
  return []
})

const currentIndex = computed(() => {
  if (items.value.length === 0) return -1
  if (hasIndex.value && Number.isFinite(indexParam.value)) return Math.min(Math.max(indexParam.value, 0), items.value.length - 1)
  const target = archive.value ? file.value : path.value
  return items.value.findIndex((item) => item.path === target)
})

const currentItem = computed(() => (currentIndex.value >= 0 ? items.value[currentIndex.value] : null))
const favoritePayload = computed(() => favoritePayloadFromRoute(route, name.value))
const favoriteKey = computed(() => (favoritePayload.value ? buildFavoriteKey(favoritePayload.value) : ''))
const isCurrentFavorite = computed(() => Boolean(favoriteKey.value) && store.hasFavorite(favoriteKey.value))

const hasPrev = computed(() => currentIndex.value > 0)
const hasNext = computed(() => currentIndex.value >= 0 && currentIndex.value < items.value.length - 1)
const totalCount = computed(() => {
  if (isCollection.value) {
    if (archive.value) return store.collectionArchiveListing?.total_files ?? 0
    return store.collectionListing?.total_images ?? 0
  }
  if (archive.value) return store.archiveListing?.total_files ?? 0
  return store.listing?.total_images ?? 0
})
const currentPosition = computed(() => {
  if (currentIndex.value >= 0) return currentIndex.value + 1
  if (hasIndex.value && Number.isFinite(indexParam.value) && totalCount.value > 0) return Math.min(Math.max(indexParam.value + 1, 1), totalCount.value)
  return 0
})
const showPositionBadge = computed(() => totalCount.value > 0 && currentPosition.value > 0)
const hasMore = computed(() => {
  if (isCollection.value) {
    if (archive.value) return Boolean(store.collectionArchiveListing?.has_more)
    return Boolean(store.collectionListing?.has_more)
  }
  if (archive.value) return Boolean(store.archiveListing?.has_more)
  return Boolean(store.listing?.has_more)
})
const sourceLabel = computed(() => {
  if (!favoritePayload.value) return '普通图片'
  return favoriteSourceLabel({ source_kind: favoritePayload.value.source_kind })
})
const displayPath = computed(() => (archive.value ? file.value || '-' : path.value || '-'))
const imageSizeText = computed(() => {
  const item = currentItem.value as SizedFolderItem | null
  if (!item) return '-'
  if (Number.isFinite(item.width) && Number.isFinite(item.height) && item.width && item.height) return `${item.width} × ${item.height}`
  return '-'
})

function goBack() { router.back() }
function toggleFullscreen() { viewerRef.value?.toggleFullscreen() }
async function toggleFavorite() { if (favoritePayload.value) await store.toggleFavorite(favoritePayload.value) }

function buildImageQuery(index: number, itemPath: string) {
  return buildImageRouteQuery({ index, path: archive.value ? undefined : itemPath, archive: archive.value || undefined, file: archive.value ? itemPath : undefined, folder: folder.value || (archive.value ? '' : store.currentFolder), collectionId: collectionId.value, view: viewMode.value, privacyEnabled: privacy.value })
}

function navigateTo(index: number) {
  if (index < 0 || index >= items.value.length) return
  router.replace({ path: '/image', query: buildImageQuery(index, items.value[index].path) })
}

function goPrev() { navigateTo(currentIndex.value - 1) }

async function goNext() {
  if (hasNext.value) { navigateTo(currentIndex.value + 1); return }
  if (!hasMore.value) return
  if (isCollection.value) {
    if (archive.value && store.collectionArchiveListing) {
      await store.loadCollectionArchive(collectionId.value as number, archive.value, store.collectionArchiveListing.page + 1, store.collectionArchiveListing.page_size, true)
      navigateTo(currentIndex.value + 1)
    } else if (!archive.value && store.collectionListing) {
      await store.loadCollectionFolder(collectionId.value as number, folder.value || store.collectionFolder, store.collectionListing.page + 1, store.collectionListing.page_size, true, viewMode.value)
      navigateTo(currentIndex.value + 1)
    }
    return
  }
  if (archive.value && store.archiveListing) {
    await store.loadArchive(archive.value, store.archiveListing.page + 1, store.archiveListing.page_size, true)
    navigateTo(currentIndex.value + 1)
  } else if (!archive.value && store.listing) {
    await store.loadFolder(folder.value || store.currentFolder, store.listing.page + 1, store.listing.page_size, true)
    navigateTo(currentIndex.value + 1)
  }
}

function handleKey(event: KeyboardEvent) {
  if (event.key === 'ArrowLeft') goPrev()
  if (event.key === 'ArrowRight') goNext()
  if (event.key === 'Escape') { if (infoVisible.value) { infoVisible.value = false; return }; goBack() }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKey)
  store.loadFavorites()
  if (isCollection.value) {
    if (archive.value) {
      if (!store.collectionArchiveListing || store.collectionArchiveListing.archive !== archive.value) await store.loadCollectionArchive(collectionId.value as number, archive.value)
    } else if (path.value) {
      const tf = folder.value || getParentFolderFromPath(path.value)
      if (!store.collectionListing || store.collectionListing.folder !== tf) await store.loadCollectionFolder(collectionId.value as number, tf, 1, 20, false, viewMode.value)
    }
    return
  }
  if (archive.value) {
    if (!store.archiveListing || store.archiveListing.archive !== archive.value) await store.loadArchive(archive.value)
  } else if (path.value) {
    const tf = folder.value || getParentFolderFromPath(path.value)
    if (!store.listing || store.listing.folder !== tf) await store.loadFolder(tf)
  }
})

onUnmounted(() => { window.removeEventListener('keydown', handleKey) })
</script>

<style scoped>
.image-page {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  height: 100dvh;
  width: 100%;
  padding-top: calc(36px + var(--safe-area-top));
  padding-bottom: calc(72px + var(--safe-area-bottom));
}

.top-title {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  height: 36px;
  padding: var(--safe-area-top) 14px 0;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

.v-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  padding: 0;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.12s;
  -webkit-tap-highlight-color: transparent;
}

.v-btn svg {
  display: block;
}
.v-btn:hover { background: rgba(0, 0, 0, 0.06); }
.v-btn:active { background: rgba(0, 0, 0, 0.10); }

.v-btn--off {
  opacity: 0.25;
  pointer-events: none;
}

.v-btn--on { color: #c2654b; }
.v-btn--on svg { fill: #c2654b; stroke: #c2654b; }

.v-filename {
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  max-width: 280px;
}

.v-pos {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  font-variant-numeric: tabular-nums;
  padding: 0 8px;
  flex-shrink: 0;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: calc(72px + var(--safe-area-bottom));
  padding: 0 14px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--stroke);
}

.bb-left,
.bb-right {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.bb-center {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.bb-divider {
  width: 1px;
  height: 24px;
  background: var(--stroke);
  flex-shrink: 0;
}

.bb-pos {
  display: inline-flex;
  align-items: baseline;
  gap: 1px;
  font-variant-numeric: tabular-nums;
  min-width: 48px;
  justify-content: center;
}

.bb-pos--empty {
  min-width: 48px;
}

.v-pos-curr {
  font-size: 11px;
  font-weight: 400;
  color: var(--muted);
}

.v-pos-div {
  font-size: 11px;
  color: var(--muted);
  margin: 0 1px;
}

.v-pos-total {
  font-size: 11px;
  color: var(--muted);
}

.v-btn--nav {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.viewer-wrap {
  flex: 1;
  position: relative;
  min-height: 0;
  display: flex;
  align-items: stretch;
  justify-content: center;
  padding: 0;
}

.viewer-wrap :deep(.viewer) {
  width: 100%;
  height: 100%;
  max-width: 100%;
}

.viewer-wrap :deep(.stage) {
  min-height: 0;
  width: 100%;
  background: transparent !important;
}

 .viewer-wrap :deep(.stage img) {
   max-height: 100%;
   max-width: 100%;
 }

.viewer-wrap :deep(.caption) { display: none; }
.viewer-wrap :deep(.hints) { display: none; }

.info-list { display: grid; gap: 14px; }
.info-item { display: grid; gap: 4px; }
.info-label { font-size: 12px; color: var(--muted); }
.info-value { font-size: 13px; color: var(--ink); word-break: break-all; }

@media (max-width: 960px) {
  .image-page {
    padding-top: calc(32px + var(--safe-area-top));
    padding-bottom: calc(60px + var(--safe-area-bottom));
  }

  .top-title {
    height: 32px;
    padding: var(--safe-area-top) 10px 0;
    font-size: 12px;
  }

  .bottom-bar {
    height: calc(60px + var(--safe-area-bottom));
    padding: 0 12px;
  }

  .v-btn {
    width: 34px;
    height: 34px;
  }

  .v-btn--nav {
    width: 30px;
    height: 30px;
  }

  .v-filename {
    max-width: 140px;
    font-size: 12px;
  }

  .v-pos-curr { font-size: 11px; }
  .bb-pos { min-width: 40px; }
  .bb-pos--empty { min-width: 40px; }
  .bb-divider { height: 20px; }
}
</style>
