<template>
  <div class="page image-page">
    <div class="viewer-bar">
      <button class="v-btn" @click="goBack" aria-label="返回">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path d="M15 6l-6 6l6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <div class="v-filename">{{ name }}</div>

      <div class="v-spacer"></div>

      <span v-if="showPositionBadge" class="v-pos">
        <span class="v-pos-curr">{{ currentPosition }}</span>
        <span class="v-pos-of">/</span>
        <span class="v-pos-total">{{ totalCount }}</span>
      </span>

      <button class="v-btn" :class="{ 'v-btn--on': isCurrentFavorite }" @click="toggleFavorite" aria-label="收藏">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path d="M12 20.4l-1.1-.98C6.05 15.1 3 12.36 3 9.02C3 6.3 5.14 4.2 7.84 4.2c1.53 0 3 .72 3.96 1.85A5.07 5.07 0 0 1 15.76 4.2C18.46 4.2 20.6 6.3 20.6 9.02c0 3.34-3.05 6.08-7.9 10.4L12 20.4z"/>
        </svg>
      </button>

      <button class="v-btn" @click="infoVisible = true" aria-label="信息">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
          <line x1="12" y1="8" x2="12" y2="8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          <line x1="12" y1="11" x2="12" y2="16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>

      <button class="v-btn" @click="toggleFullscreen" aria-label="全屏">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <polyline points="15 3 21 3 21 9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="9 21 3 21 3 15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="21" y1="3" x2="14" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <line x1="3" y1="21" x2="10" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div class="viewer-wrap">
      <button class="v-arrow v-arrow--l" :class="{ 'v-arrow--off': !hasPrev }" :disabled="!hasPrev" @click="goPrev" aria-label="上一张">
        <svg viewBox="0 0 24 24" width="24" height="24"><path d="M15 6l-6 6l6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>

      <ImageViewer
        ref="viewerRef"
        :src="src"
        :name="name"
        @scale-change="scale = $event"
        @fullscreen-change="isFullscreen = $event"
      />

      <button class="v-arrow v-arrow--r" :class="{ 'v-arrow--off': !hasNext }" :disabled="!hasNext" @click="goNext" aria-label="下一张">
        <svg viewBox="0 0 24 24" width="24" height="24"><path d="M9 6l6 6l-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
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
   padding-top: calc(48px + var(--safe-area-top));
 }

 .viewer-bar {
   position: fixed;
   top: 0;
   left: 0;
   right: 0;
   z-index: 20;
   display: flex;
   align-items: center;
   gap: 2px;
   height: 48px;
   padding: var(--safe-area-top) 14px 0;
   background: rgba(255, 255, 255, 0.82);
   backdrop-filter: blur(12px);
   -webkit-backdrop-filter: blur(12px);
   border-bottom: 1px solid var(--stroke);
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
  color: var(--ink);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.12s;
  -webkit-tap-highlight-color: transparent;
}

.v-btn:hover { background: rgba(0, 0, 0, 0.06); }
.v-btn:active { background: rgba(0, 0, 0, 0.10); }

.v-btn--on { color: #c2654b; }
.v-btn--on svg { fill: #c2654b; stroke: #c2654b; }

.v-filename {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  max-width: 280px;
}

.v-spacer {
  flex: 1;
  min-width: 8px;
}

.v-pos {
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
  font-variant-numeric: tabular-nums;
  padding: 0 8px;
  flex-shrink: 0;
}

.v-pos-curr {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink);
}

.v-pos-of {
  font-size: 11px;
  color: var(--muted);
  margin: 0 1px;
}

.v-pos-total {
  font-size: 11px;
  color: var(--muted);
}

.viewer-wrap {
  flex: 1;
  position: relative;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 58px;
}

.v-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(8px);
  color: var(--ink);
  cursor: pointer;
  transition: opacity 0.18s, transform 0.18s, background 0.12s;
  -webkit-tap-highlight-color: transparent;
}

.v-arrow--l { left: 8px; }
.v-arrow--r { right: 8px; }

.v-arrow:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.94);
  transform: translateY(-50%) scale(1.08);
}

.v-arrow:active:not(:disabled) {
  transform: translateY(-50%) scale(0.96);
}

.v-arrow--off {
  opacity: 0;
  pointer-events: none;
}

.v-arrow:disabled {
  opacity: 0.25;
  cursor: default;
}

.viewer-wrap :deep(.viewer) {
  width: 100%;
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
     padding-top: calc(44px + var(--safe-area-top));
   }

   .viewer-bar {
     height: 44px;
     padding: var(--safe-area-top) 10px 0;
   }

  .v-btn {
    width: 36px;
    height: 36px;
  }

  .v-filename {
    max-width: 140px;
    font-size: 12px;
  }

  .viewer-wrap {
    padding: 0 48px;
  }

  .v-arrow {
    width: 36px;
    height: 36px;
  }

  .v-arrow--l { left: 4px; }
  .v-arrow--r { right: 4px; }

   .v-pos-curr { font-size: 12px; }
  .v-pos { padding: 0 6px; }
}
</style>
