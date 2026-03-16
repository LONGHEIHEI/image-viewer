<template>
  <div class="page image-page">
    <div class="page-header">
      <div class="page-actions">
        <span v-if="showPositionBadge" class="viewer-position-badge">
          <span class="viewer-position-current">{{ currentPosition }}</span>
          <span class="viewer-position-divider">/</span>
          <span class="viewer-position-total">{{ totalCount }}</span>
        </span>
        <n-button size="small" :disabled="!hasPrev" @click="goPrev">上一张</n-button>
        <n-button size="small" :disabled="!hasNext" @click="goNext">下一张</n-button>
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton } from 'naive-ui'
import {
  archiveImageUrl,
  imageUrl,
  collectionImageUrl,
  collectionArchiveImageUrl
} from '../api/client'
import { useGalleryStore } from '../store/gallery'
import ImageViewer from '../components/ImageViewer.vue'

type ViewerExpose = {
  toggleFullscreen: () => void
  resetView: () => void
}

const viewerRef = ref<ViewerExpose | null>(null)
const scale = ref(1)
const isFullscreen = ref(false)

const route = useRoute()
const router = useRouter()
const store = useGalleryStore()

const path = computed(() => String(route.query.path || ''))
const archive = computed(() => String(route.query.archive || ''))
const file = computed(() => String(route.query.file || ''))
const folder = computed(() => String(route.query.folder || ''))
const hasIndex = computed(() => route.query.index !== undefined)
const indexParam = computed(() => (hasIndex.value ? Number(route.query.index) : -1))

const collectionId = computed(() => {
  const raw = route.query.collection
  if (raw === undefined || raw === null || raw === '') return null
  const num = Number(raw)
  return Number.isFinite(num) ? num : null
})

const viewMode = computed(() => String(route.query.view || 'folder'))

const isCollection = computed(() => collectionId.value !== null)

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

const name = computed(() => file.value || path.value.split('/').pop() || '')

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

function goBack() {
  router.back()
}

function resetView() {
  viewerRef.value?.resetView()
}

function toggleFullscreen() {
  viewerRef.value?.toggleFullscreen()
}

function navigateTo(index: number) {
  if (index < 0 || index >= items.value.length) return
  const item = items.value[index]
  if (archive.value) {
    const query: Record<string, string> = { archive: archive.value, file: item.path, index: String(index) }
    if (folder.value) {
      query.folder = folder.value
    }
    if (isCollection.value) {
      query.collection = String(collectionId.value)
      query.view = viewMode.value
    }
    router.replace({ path: '/image', query })
  } else {
    const query: Record<string, string> = {
      path: item.path,
      index: String(index),
      folder: folder.value || store.currentFolder
    }
    if (isCollection.value) {
      query.collection = String(collectionId.value)
      query.view = viewMode.value
    }
    router.replace({ path: '/image', query })
  }
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
        viewMode.value === 'flat' ? 'flat' : 'folder'
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
    goBack()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKey)
  if (isCollection.value) {
    if (archive.value) {
      if (!store.collectionArchiveListing || store.collectionArchiveListing.archive !== archive.value) {
        await store.loadCollectionArchive(collectionId.value as number, archive.value)
      }
    } else if (path.value) {
      const targetFolder = folder.value || path.value.split('/').slice(0, -1).join('/')
      if (!store.collectionListing || store.collectionListing.folder !== targetFolder) {
        await store.loadCollectionFolder(
          collectionId.value as number,
          targetFolder,
          1,
          20,
          false,
          viewMode.value === 'flat' ? 'flat' : 'folder'
        )
      }
    }
    return
  }
  if (archive.value) {
    if (!store.archiveListing || store.archiveListing.archive !== archive.value) {
      await store.loadArchive(archive.value)
    }
  } else if (path.value) {
    const targetFolder = folder.value || path.value.split('/').slice(0, -1).join('/')
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

@media (max-width: 960px) {
  .image-page {
    min-height: auto;
  }

  .page-header {
    position: fixed;
    left: calc(10px + env(safe-area-inset-left));
    right: calc(10px + env(safe-area-inset-right));
    bottom: calc(12px + env(safe-area-inset-bottom));
    z-index: 15;
    margin: 0;
    justify-content: center;
    pointer-events: none;
  }

  .page-actions {
    width: auto;
    max-width: 100%;
    justify-content: center;
    padding: 8px 10px;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(27, 30, 39, 0.08);
    box-shadow: 0 14px 30px rgba(20, 25, 35, 0.14);
    backdrop-filter: blur(16px);
    pointer-events: auto;
  }

  .viewer-position-badge {
    min-height: 26px;
    padding: 0;
  }

  .viewer-position-current {
    font-size: 14px;
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
