<template>
  <div class="page">
    <section v-if="listing" class="archive-browser">
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
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NButton, NInput } from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import ImageGrid from '../components/ImageGrid.vue'
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

const listing = computed(() =>
  isCollection.value ? store.collectionArchiveListing : store.archiveListing
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
}
</style>
