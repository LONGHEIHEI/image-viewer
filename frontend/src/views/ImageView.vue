<template>
  <div>
    <div class="topbar">
      <button class="ghost" @click="goBack">返回</button>
      <div class="actions">
        <button class="ghost" :disabled="!hasPrev" @click="goPrev">上一张</button>
        <button class="ghost" :disabled="!hasNext" @click="goNext">下一张</button>
      </div>
    </div>
    <ImageViewer :src="src" :name="name" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { archiveImageUrl, imageUrl } from '../api/client'
import { useGalleryStore } from '../store/gallery'
import ImageViewer from '../components/ImageViewer.vue'

const route = useRoute()
const router = useRouter()
const store = useGalleryStore()

const path = computed(() => String(route.query.path || ''))
const archive = computed(() => String(route.query.archive || ''))
const file = computed(() => String(route.query.file || ''))
const folder = computed(() => String(route.query.folder || ''))
const hasIndex = computed(() => route.query.index !== undefined)
const indexParam = computed(() => (hasIndex.value ? Number(route.query.index) : -1))

const src = computed(() => {
  if (archive.value && file.value) {
    return archiveImageUrl(archive.value, file.value)
  }
  return imageUrl(path.value)
})

const name = computed(() => file.value || path.value.split('/').pop() || '')

const items = computed(() => {
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
  if (archive.value) return Boolean(store.archiveListing?.has_more)
  return Boolean(store.listing?.has_more)
})

function goBack() {
  router.back()
}

function navigateTo(index: number) {
  if (index < 0 || index >= items.value.length) return
  const item = items.value[index]
  if (archive.value) {
    router.replace({ path: '/image', query: { archive: archive.value, file: item.path, index: String(index) } })
  } else {
    router.replace({
      path: '/image',
      query: { path: item.path, index: String(index), folder: folder.value || store.currentFolder }
    })
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
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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

.ghost:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
