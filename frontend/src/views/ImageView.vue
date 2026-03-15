<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">图片预览</div>
      <div class="page-actions">
        <n-button size="small" @click="goBack">返回</n-button>
        <n-button size="small" :disabled="!hasPrev" @click="goPrev">上一张</n-button>
        <n-button size="small" :disabled="!hasNext" @click="goNext">下一张</n-button>
        <n-button size="small" @click="toggleFullscreen">
          {{ isFullscreen ? '退出全屏' : '全屏' }}
        </n-button>
        <n-button size="small" @click="resetView">重置</n-button>
        <span class="zoom">{{ Math.round(scale * 100) }}%</span>
      </div>
    </div>
    <n-card class="panel" :bordered="false">
      <ImageViewer
        ref="viewerRef"
        :src="src"
        :name="name"
        @scale-change="scale = $event"
        @fullscreen-change="isFullscreen = $event"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NCard } from 'naive-ui'
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
    if (isCollection.value) {
      query.collection = String(collectionId.value)
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
        true
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
        await store.loadCollectionFolder(collectionId.value as number, targetFolder)
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
.zoom {
  font-size: 12px;
  color: var(--muted);
}
</style>
