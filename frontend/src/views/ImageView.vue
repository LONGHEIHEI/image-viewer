<template>
  <div class="page image-page page--floating-action">
    <div class="page-header">
      <div class="page-actions">
        <span v-if="showPositionBadge" class="viewer-position-badge">
          <span class="viewer-position-current">{{ currentPosition }}</span>
          <span class="viewer-position-divider">/</span>
          <span class="viewer-position-total">{{ totalCount }}</span>
        </span>
        <n-button size="small" :disabled="!hasPrev" @click="goPrev">上一张</n-button>
        <n-button size="small" :disabled="!hasNext" @click="goNext">下一张</n-button>
        <n-button
          size="small"
          class="viewer-favorite-button"
          :type="isCurrentFavorite ? 'primary' : 'default'"
          @click="toggleFavorite"
        >
          <template #icon>
            <svg viewBox="0 0 24 24" class="viewer-favorite-icon" aria-hidden="true">
              <path
                d="M12 20.4l-1.1-.98C6.05 15.1 3 12.36 3 9.02C3 6.3 5.14 4.2 7.84 4.2c1.53 0 3 .72 3.96 1.85A5.07 5.07 0 0 1 15.76 4.2C18.46 4.2 20.6 6.3 20.6 9.02c0 3.34-3.05 6.08-7.9 10.4L12 20.4z"
              />
            </svg>
          </template>
          {{ isCurrentFavorite ? '已收藏' : '收藏' }}
        </n-button>
        <n-button size="small" @click="infoVisible = true">信息</n-button>
        <n-button size="small" @click="toggleFullscreen">
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </n-button>
        <n-button size="small" @click="resetView">重置</n-button>
        <span class="zoom">{{ Math.round(scale * 100) }}%</span>
      </div>
    </div>
    <div class="viewer-shell">
      <ImageViewer
        ref="viewerRef"
        :src="src"
        :name="name"
        @scale-change="scale = $event"
        @fullscreen-change="isFullscreen = $event"
      />
    </div>

    <n-drawer v-model:show="infoVisible" placement="right" :width="drawerWidth">
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NDrawer, NDrawerContent } from 'naive-ui'
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
const drawerWidth = computed(() => (typeof window !== 'undefined' && window.innerWidth <= 960 ? '84vw' : 420))

const src = computed(() => {
  if (archive.value && file.value) {
    if (isCollection.value) {
      return collectionArchiveImageUrl(collectionId.value as number, archive.value, file.value)
    }
    return archiveImageUrl(archive.value, file.value)
  }
  if (isCollection.value) {
    return collectionImageUrl(collectionId.value as number, path.value)
  }
  return imageUrl(path.value)
})

const name = computed(() => file.value || getPathBasename(path.value))

const items = computed(() => {
  if (isCollection.value) {
    if (archive.value && store.collectionArchiveListing?.archive === archive.value) {
      return store.collectionArchiveListing.files
    }
    if (!archive.value && store.collectionListing?.folder === (folder.value || store.collectionFolder)) {
      return store.collectionListing.images
    }
    return []
  }
  if (archive.value && store.archiveListing?.archive === archive.value) {
    return store.archiveListing.files
  }
  if (!archive.value && store.listing?.folder === (folder.value || store.currentFolder)) {
    return store.listing.images
  }
  return []
})

const currentIndex = computed(() => {
  if (items.value.length === 0) return -1
  if (hasIndex.value && Number.isFinite(indexParam.value)) {
    return Math.min(Math.max(indexParam.value, 0), items.value.length - 1)
  }
  const target = archive.value ? file.value : path.value
  return items.value.findIndex((item) => item.path === target)
})

const currentItem = computed(() => (currentIndex.value >= 0 ? items.value[currentIndex.value] : null))
const favoritePayload = computed(() => favoritePayloadFromRoute(route, name.value))
const favoriteKey = computed(() => (favoritePayload.value ? buildFavoriteKey(favoritePayload.value) : ''))
const isCurrentFavorite = computed(
  () => Boolean(favoriteKey.value) && store.hasFavorite(favoriteKey.value)
)

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
  if (hasIndex.value && Number.isFinite(indexParam.value) && totalCount.value > 0) {
    return Math.min(Math.max(indexParam.value + 1, 1), totalCount.value)
  }
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
  if (Number.isFinite(item.width) && Number.isFinite(item.height) && item.width && item.height) {
    return `${item.width} × ${item.height}`
  }
  return '-'
})

function goBack() {
  router.back()
}

function resetView() {
  viewerRef.value?.resetView()
}

function toggleFullscreen() {
  viewerRef.value?.toggleFullscreen()
}

async function toggleFavorite() {
  if (!favoritePayload.value) return
  await store.toggleFavorite(favoritePayload.value)
}

function buildImageQuery(index: number, itemPath: string) {
  return buildImageRouteQuery({
    index,
    path: archive.value ? undefined : itemPath,
    archive: archive.value || undefined,
    file: archive.value ? itemPath : undefined,
    folder: folder.value || (archive.value ? '' : store.currentFolder),
    collectionId: collectionId.value,
    view: viewMode.value,
    privacyEnabled: privacy.value
  })
}

function navigateTo(index: number) {
  if (index < 0 || index >= items.value.length) return
  const item = items.value[index]
  router.replace({ path: '/image', query: buildImageQuery(index, item.path) })
}

function goPrev() {
  navigateTo(currentIndex.value - 1)
}

async function goNext() {
  if (hasNext.value) {
    navigateTo(currentIndex.value + 1)
    return
  }
  if (!hasMore.value) return
  if (isCollection.value) {
    if (archive.value && store.collectionArchiveListing) {
      await store.loadCollectionArchive(
        collectionId.value as number,
        archive.value,
        store.collectionArchiveListing.page + 1,
        store.collectionArchiveListing.page_size,
        true
      )
      navigateTo(currentIndex.value + 1)
      return
    }
    if (!archive.value && store.collectionListing) {
      await store.loadCollectionFolder(
        collectionId.value as number,
        folder.value || store.collectionFolder,
        store.collectionListing.page + 1,
        store.collectionListing.page_size,
        true,
        viewMode.value
      )
      navigateTo(currentIndex.value + 1)
    }
    return
  }
  if (archive.value && store.archiveListing) {
    await store.loadArchive(
      archive.value,
      store.archiveListing.page + 1,
      store.archiveListing.page_size,
      true
    )
    navigateTo(currentIndex.value + 1)
    return
  }
  if (!archive.value && store.listing) {
    await store.loadFolder(
      folder.value || store.currentFolder,
      store.listing.page + 1,
      store.listing.page_size,
      true
    )
    navigateTo(currentIndex.value + 1)
  }
}

function handleKey(event: KeyboardEvent) {
  if (event.key === 'ArrowLeft') {
    goPrev()
  }
  if (event.key === 'ArrowRight') {
    goNext()
  }
  if (event.key === 'Escape') {
    if (infoVisible.value) {
      infoVisible.value = false
      return
    }
    goBack()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKey)
  store.loadFavorites()
  if (isCollection.value) {
    if (archive.value) {
      if (!store.collectionArchiveListing || store.collectionArchiveListing.archive !== archive.value) {
        await store.loadCollectionArchive(collectionId.value as number, archive.value)
      }
    } else if (path.value) {
      const targetFolder = folder.value || getParentFolderFromPath(path.value)
      if (!store.collectionListing || store.collectionListing.folder !== targetFolder) {
        await store.loadCollectionFolder(collectionId.value as number, targetFolder, 1, 20, false, viewMode.value)
      }
    }
    return
  }
  if (archive.value) {
    if (!store.archiveListing || store.archiveListing.archive !== archive.value) {
      await store.loadArchive(archive.value)
    }
  } else if (path.value) {
    const targetFolder = folder.value || getParentFolderFromPath(path.value)
    if (!store.listing || store.listing.folder !== targetFolder) {
      await store.loadFolder(targetFolder)
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKey)
})
</script>

<style scoped>
.image-page {
  min-height: calc(100dvh - 72px);
  gap: 0;
}

.page-header {
  margin-bottom: 14px;
}

.viewer-shell {
  display: grid;
  min-width: 0;
  min-height: calc(100dvh - 180px);
  padding-top: 6px;
}

.viewer-position-badge {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  min-height: 28px;
  padding: 0 2px;
  color: var(--ink);
  white-space: nowrap;
}

.viewer-position-current {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 15px;
  font-weight: 700;
  color: rgba(27, 30, 39, 0.88);
  letter-spacing: 0.01em;
}

.viewer-position-divider {
  font-size: 12px;
  font-weight: 700;
  color: rgba(92, 102, 114, 0.46);
}

.viewer-position-total {
  font-size: 12px;
  font-weight: 700;
  color: rgba(92, 102, 114, 0.78);
}

.viewer-favorite-button {
  min-width: 82px;
}

.viewer-favorite-icon {
  width: 15px;
  height: 15px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.9;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.viewer-favorite-button:deep(.n-button__icon) {
  margin-right: 4px;
}

.viewer-favorite-button.n-button--primary .viewer-favorite-icon {
  fill: currentColor;
  stroke: rgba(255, 255, 255, 0.72);
}

.info-list {
  display: grid;
  gap: 14px;
}

.info-item {
  display: grid;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--muted);
}

.info-value {
  font-size: 13px;
  color: var(--ink);
  word-break: break-all;
}

@media (max-width: 960px) {
  .image-page {
    min-height: auto;
  }

  .page-header {
    position: fixed;
    left: calc(10px + var(--safe-area-left));
    right: calc(10px + var(--safe-area-right));
    bottom: calc(10px + var(--safe-area-bottom));
    z-index: 15;
    margin: 0;
    justify-content: center;
    pointer-events: none;
  }

  .page-actions {
    width: min(100%, 560px);
    max-width: 100%;
    justify-content: flex-start;
    padding: 8px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(27, 30, 39, 0.08);
    box-shadow: 0 14px 30px rgba(20, 25, 35, 0.14);
    backdrop-filter: blur(16px);
    pointer-events: auto;
  }

  .viewer-shell {
    min-height: calc(100dvh - 154px - var(--safe-area-top) - var(--safe-area-bottom));
    padding-top: 0;
  }

  .viewer-position-badge {
    min-height: 26px;
    padding: 0;
  }

  .viewer-position-current {
    font-size: 14px;
  }

  .viewer-favorite-button {
    min-width: 0;
  }

  .zoom {
    display: none;
  }
}

.zoom {
  font-size: 12px;
  color: var(--muted);
}
</style>
