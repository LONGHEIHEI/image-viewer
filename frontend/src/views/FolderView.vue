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
      <div class="browser-mobile-bar">
        <div v-if="archiveLabel" class="browser-mobile-caption">{{ archiveLabel }}</div>
        <n-input
          v-model:value="searchTerm"
          class="panel-search panel-search--mobile"
          placeholder="搜索压缩包内图片"
          clearable
        />
      </div>
      <div class="panel-header browser-header browser-header--mobile-hidden">
        <div class="browser-main">
          <div class="panel-left" v-if="archiveLabel">
            <div class="panel-subtitle mobile-topbar-title-hidden">{{ archiveLabel }}</div>
          </div>
          <n-input
            v-model:value="searchTerm"
            class="panel-search"
            placeholder="搜索压缩包内图片"
            clearable
          />
        </div>
        <div class="browser-side">
          <div class="meta" v-if="listing.total_files">
            共 {{ listing.total_files }} 张 · 第 {{ listing.page }} 页
          </div>
          <n-button size="small" @click="goBack">返回</n-button>
        </div>
      </div>
      <ImageGrid
        :images="filteredFiles"
        :thumb="thumb"
        :privacy-enabled="privacyEnabled"
        :privacy-storage-key="privacyStorageKey"
        @open-image="openArchiveImage"
      />
      <div class="load" v-if="listing.has_more">
        <n-button type="primary" :loading="store.loading" @click="loadMore">加载更多</n-button>
      </div>
    </section>

    <div v-if="store.error" class="error">{{ store.error }}</div>
    <div v-if="store.loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NInput } from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import ImageGrid from '../components/ImageGrid.vue'
import PrivacyRevealButton from '../components/PrivacyRevealButton.vue'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'
import { archiveThumbUrl, collectionArchiveThumbUrl, getCollectionInfo } from '../api/client'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()

const archive = computed(() => String(route.query.archive || ''))
const folder = computed(() => String(route.query.folder || ''))
const searchTerm = ref('')

const collectionId = computed(() => {
  const raw = route.query.collection
  if (raw === undefined || raw === null || raw === '') return null
  const num = Number(raw)
  return Number.isFinite(num) ? num : null
})

const isCollection = computed(() => collectionId.value !== null)
const collectionView = computed(() => String(route.query.view || 'folder'))
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
  const parts = archive.value.split(/[\\/]+/).filter(Boolean)
  return parts[parts.length - 1] || archive.value
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

const filteredFiles = computed(() => {
  if (!listing.value) return []
  if (!searchTerm.value.trim()) return listing.value.files
  const keyword = searchTerm.value.toLowerCase()
  return listing.value.files.filter((file) => file.name.toLowerCase().includes(keyword))
})

function openArchiveImage(file: string) {
  const baseIndex = listing.value?.files.findIndex((item) => item.path === file) ?? 0
  const query: Record<string, string> = {
    archive: archive.value,
    file,
    index: String(baseIndex)
  }
  if (folder.value) {
    query.folder = folder.value
  }
  if (isCollection.value) {
    query.collection = String(collectionId.value)
    query.view = collectionView.value
    if (privacyEnabled.value) {
      query.privacy = '1'
    }
  }
  router.push({ path: '/image', query })
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

.browser-mobile-bar {
  display: none;
}

.privacy-toolbar {
  position: fixed;
  right: calc(20px + env(safe-area-inset-right));
  bottom: calc(22px + env(safe-area-inset-bottom));
  z-index: 40;
}

.browser-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.browser-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  flex-wrap: wrap;
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.browser-side {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.panel-subtitle {
  font-size: 12px;
  color: var(--muted);
  font-weight: 700;
  letter-spacing: 0.01em;
}

.panel-search {
  width: 320px;
  max-width: 40vw;
  --n-color: #fafafa;
  --n-color-focus: #fff;
  --n-color-hover: #fdfdfd;
  --n-border: rgba(27, 30, 39, 0.08);
  --n-border-hover: rgba(27, 30, 39, 0.12);
  --n-border-focus: rgba(27, 30, 39, 0.18);
  --n-box-shadow-focus: none;
}

@media (max-width: 960px) {
  .browser-header--mobile-hidden {
    display: none;
  }

  .browser-mobile-bar {
    display: grid;
    gap: 8px;
  }

  .browser-mobile-caption {
    font-size: 12px;
    font-weight: 700;
    color: var(--muted);
    line-height: 1.3;
    word-break: break-word;
  }

  .browser-header,
  .browser-main,
  .browser-side {
    align-items: flex-start;
  }

  .browser-side {
    width: 100%;
    justify-content: space-between;
  }

  .panel-search {
    width: 100%;
    max-width: none;
  }

  .panel-search--mobile {
    width: 100%;
  }

  .privacy-toolbar {
    right: calc(14px + env(safe-area-inset-right));
    bottom: calc(16px + env(safe-area-inset-bottom));
  }
}
</style>
