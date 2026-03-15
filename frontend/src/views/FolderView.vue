<template>
  <div class="page">
    <n-card v-if="listing" class="panel panel-tight" :bordered="false">
      <div class="panel-header panel-stack">
        <div class="panel-row panel-row-top">
          <div class="panel-left">
            <div class="panel-title">图片</div>
            <div class="panel-subtitle" v-if="archiveLabel">{{ archiveLabel }}</div>
          </div>
          <div class="panel-right">
            <n-button size="small" @click="goBack">返回</n-button>
          </div>
        </div>
        <div class="panel-row panel-row-bottom">
          <n-input
            v-model:value="searchTerm"
            class="panel-search"
            placeholder="搜索压缩包内图片"
            clearable
          />
          <div class="meta" v-if="listing.total_files">
            共 {{ listing.total_files }} 张 · 第 {{ listing.page }} 页
          </div>
        </div>
      </div>
      <ImageGrid :images="filteredFiles" :thumb="thumb" @open-image="openArchiveImage" />
      <div class="load" v-if="listing.has_more">
        <n-button type="primary" :loading="store.loading" @click="loadMore">加载更多</n-button>
      </div>
    </n-card>

    <div v-if="store.error" class="error">{{ store.error }}</div>
    <div v-if="store.loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NButton, NInput } from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import ImageGrid from '../components/ImageGrid.vue'
import { archiveThumbUrl, collectionArchiveThumbUrl } from '../api/client'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()

const archive = computed(() => String(route.query.archive || ''))
const searchTerm = ref('')

const collectionId = computed(() => {
  const raw = route.query.collection
  if (raw === undefined || raw === null || raw === '') return null
  const num = Number(raw)
  return Number.isFinite(num) ? num : null
})

const isCollection = computed(() => collectionId.value !== null)

const listing = computed(() =>
  isCollection.value ? store.collectionArchiveListing : store.archiveListing
)

const archiveLabel = computed(() => {
  if (!archive.value) return ''
  const parts = archive.value.split(/[\\/]+/).filter(Boolean)
  return parts[parts.length - 1] || archive.value
})

onMounted(() => {
  if (!archive.value) return
  if (isCollection.value) {
    store.loadCollectionArchive(collectionId.value as number, archive.value)
  } else {
    store.loadArchive(archive.value)
  }
})

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
  if (isCollection.value) {
    query.collection = String(collectionId.value)
  }
  router.push({ path: '/image', query })
}

function goBack() {
  if (isCollection.value) {
    router.push(`/collection/${collectionId.value}`)
    return
  }
  router.push('/')
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
.panel-tight :deep(.n-card__content) {
  padding-top: 16px;
}

.panel-stack {
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
}

.panel-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-row-top {
  justify-content: space-between;
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.panel-right {
  display: flex;
  justify-content: flex-end;
}

.panel-subtitle {
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
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
  .panel-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .panel-search {
    width: 100%;
    max-width: none;
  }
}
</style>
