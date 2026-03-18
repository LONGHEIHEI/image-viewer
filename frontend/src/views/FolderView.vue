<template>
  <div :class="['page', { 'page--floating-action': showPrivacyToggleButton }]">
    <section v-if="listing" class="archive-browser">
      <div v-if="showPrivacyToggleButton" class="privacy-toolbar">
        <PrivacyRevealButton
          :title="privacyToggleTitle"
          :active="allCurrentRevealed"
          @click="toggleCurrentArchivePrivacy"
        />
      </div>
      <ImageBrowserSection
        :images="listing.files"
        :thumb="thumb"
        :subtitle="archiveLabel"
        :meta-text="listing.total_files ? `共 ${listing.total_files} 张 · 第 ${listing.page} 页` : ''"
        search-enabled
        search-placeholder="搜索压缩包内图片"
        :search-scope-key="archive"
        show-back-button
        :has-more="listing.has_more"
        :loading="store.loading"
        :privacy-enabled="privacyEnabled"
        :privacy-storage-key="privacyStorageKey"
        favorite-enabled
        :is-favorite="isFavorite"
        :toggle-favorite="toggleFavorite"
        @open-image="openArchiveImage"
        @back="goBack"
        @load-more="loadMore"
      />
    </section>

    <div v-if="store.error" class="error">{{ store.error }}</div>
    <div v-if="store.loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGalleryStore } from '../store/gallery'
import PrivacyRevealButton from '../components/PrivacyRevealButton.vue'
import ImageBrowserSection from '../components/ImageBrowserSection.vue'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'
import { buildFavoriteKey } from '../utils/favorites'
import {
  buildImageRouteQuery,
  getPathBasename,
  parseCollectionId,
  parseGalleryView,
  readQueryString
} from '../utils/galleryRoute'
import { archiveThumbUrl, collectionArchiveThumbUrl, getCollectionInfo } from '../api/client'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()

const archive = computed(() => readQueryString(route.query.archive))
const folder = computed(() => readQueryString(route.query.folder))

const collectionId = computed(() => parseCollectionId(route.query.collection))

const isCollection = computed(() => collectionId.value !== null)
const collectionView = computed(() => parseGalleryView(route.query.view))
const privacyEnabled = ref(route.query.privacy === '1')
const privacyStorageKey = computed(() =>
  isCollection.value ? `collection-privacy-${collectionId.value}` : ''
)
const { isRevealed, revealMany, hideMany, reset } = usePrivacyReveal(privacyStorageKey)
// Same semantics as CollectionView: once user taps "show current folder",
// keep revealing newly appended items until they hide again. Reset on archive change.
const autoRevealCurrentArchive = ref(false)

const listing = computed(() =>
  isCollection.value ? store.collectionArchiveListing : store.archiveListing
)
const currentPrivacyKeys = computed(() => {
  if (!listing.value || !privacyEnabled.value) {
    return [] as string[]
  }
  return listing.value.files.map((file) => `image:${file.path}`)
})

watch(
  () => `${archive.value}|${folder.value}|${String(route.query.collection || '')}|${String(route.query.view || '')}|${String(route.query.privacy || '')}`,
  () => {
    autoRevealCurrentArchive.value = false
    reset()
  }
)

watch(
  () => currentPrivacyKeys.value.length,
  () => {
    if (!autoRevealCurrentArchive.value) return
    revealMany(currentPrivacyKeys.value)
  }
)

const showPrivacyToggleButton = computed(() =>
  privacyEnabled.value && currentPrivacyKeys.value.length > 0
)

const allCurrentRevealed = computed(() =>
  currentPrivacyKeys.value.length > 0 &&
  currentPrivacyKeys.value.every((key) => isRevealed(key))
)

const privacyToggleTitle = computed(() =>
  allCurrentRevealed.value ? '隐藏当前文件夹' : '显示当前文件夹'
)

const archiveLabel = computed(() => {
  if (!archive.value) return ''
  return getPathBasename(archive.value)
})

onMounted(async () => {
  if (!archive.value) return
  if (isCollection.value) {
    await hydrateCollectionPrivacy()
    if (privacyEnabled.value) {
      // Entering a privacy-enabled archive view should always start masked.
      reset()
    }
    await store.loadCollectionArchive(collectionId.value as number, archive.value)
  } else {
    await store.loadArchive(archive.value)
  }
})

async function hydrateCollectionPrivacy() {
  if (!isCollection.value) {
    privacyEnabled.value = false
    return
  }
  if (route.query.privacy === '1') {
    privacyEnabled.value = true
    return
  }
  try {
    const info = await getCollectionInfo(collectionId.value as number)
    privacyEnabled.value = Boolean(info.privacy_enabled)
  } catch {
    privacyEnabled.value = false
  }
}

function openArchiveImage(file: string) {
  const baseIndex = listing.value?.files.findIndex((item) => item.path === file) ?? 0
  router.push({
    path: '/image',
    query: buildImageRouteQuery({
      index: baseIndex,
      archive: archive.value,
      file,
      folder: folder.value,
      collectionId: collectionId.value,
      view: collectionView.value,
      privacyEnabled: privacyEnabled.value
    })
  })
}

function favoritePayload(filePath: string) {
  const item = listing.value?.files.find((entry) => entry.path === filePath)
  return {
    source_kind: isCollection.value ? ('collection_archive_image' as const) : ('archive_image' as const),
    collection_id: collectionId.value,
    container_path: archive.value,
    item_path: filePath,
    folder_path: folder.value,
    view_mode: collectionView.value === 'flat' ? ('flat' as const) : ('folder' as const),
    item_name: item?.name || getPathBasename(filePath),
    collection_token: collectionId.value
      ? localStorage.getItem(`collection_token_${collectionId.value}`) || ''
      : ''
  }
}

function isFavorite(filePath: string) {
  return store.hasFavorite(buildFavoriteKey(favoritePayload(filePath)))
}

async function toggleFavorite(filePath: string) {
  await store.toggleFavorite(favoritePayload(filePath))
}

function goBack() {
  if (isCollection.value) {
    const query: Record<string, string> = { view: collectionView.value }
    if (folder.value) {
      query.path = folder.value
    }
    if (privacyEnabled.value) {
      query.privacy = '1'
    }
    router.push({
      path: `/collection/${collectionId.value}`,
      query
    })
    return
  }
  router.push({
    path: '/',
    query: folder.value ? { path: folder.value } : {}
  })
}

function loadMore() {
  if (!listing.value) return
  if (isCollection.value) {
    store.loadCollectionArchive(
      collectionId.value as number,
      archive.value,
      listing.value.page + 1,
      listing.value.page_size,
      true
    )
    return
  }
  store.loadArchive(archive.value, listing.value.page + 1, listing.value.page_size, true)
}

function toggleCurrentArchivePrivacy() {
  if (allCurrentRevealed.value) {
    autoRevealCurrentArchive.value = false
    hideMany(currentPrivacyKeys.value)
    return
  }
  autoRevealCurrentArchive.value = true
  revealMany(currentPrivacyKeys.value)
}

function thumb(filePath: string) {
  if (isCollection.value) {
    return collectionArchiveThumbUrl(collectionId.value as number, archive.value, filePath)
  }
  return archiveThumbUrl(archive.value, filePath)
}
</script>

<style scoped>
.archive-browser {
  display: grid;
  gap: 12px;
}

.privacy-toolbar {
  position: fixed;
  right: calc(20px + var(--safe-area-right));
  bottom: calc(22px + var(--safe-area-bottom));
  z-index: 40;
}

@media (max-width: 960px) {
  .privacy-toolbar {
    right: calc(14px + var(--safe-area-right));
    bottom: calc(16px + var(--safe-area-bottom));
  }
}
</style>
