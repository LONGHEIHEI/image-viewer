<template>
  <div>
    <div class="top">
      <button class="ghost" @click="goBack">返回</button>
      <div>
        <div class="title">压缩包</div>
        <div class="subtitle">{{ archive }}</div>
      </div>
    </div>

    <div v-if="store.archiveListing" class="panel">
      <div class="panel-header">
        <div>
          <div class="panel-title">图片</div>
          <div class="panel-sub">{{ store.archiveListing.total_files }} 张</div>
        </div>
        <div class="meta">第 {{ store.archiveListing.page }} 页</div>
      </div>
      <div class="search">
        <input v-model="searchTerm" placeholder="搜索压缩包内图片" />
        <span class="count">已显示 {{ filteredFiles.length }} 张</span>
      </div>
      <ImageGrid
        :images="filteredFiles"
        :thumb="thumb"
        @open-image="openArchiveImage"
      />
      <div class="load" v-if="store.archiveListing.has_more">
        <button class="primary" :disabled="store.loading" @click="loadMore">加载更多</button>
      </div>
    </div>

    <div v-if="store.error" class="error">{{ store.error }}</div>
    <div v-if="store.loading" class="loading">加载中...</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGalleryStore } from '../store/gallery'
import ImageGrid from '../components/ImageGrid.vue'
import { archiveThumbUrl } from '../api/client'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()

const archive = String(route.query.archive || '')
const searchTerm = ref('')

onMounted(() => {
  if (archive) {
    store.loadArchive(archive)
  }
})

const filteredFiles = computed(() => {
  if (!store.archiveListing) return []
  if (!searchTerm.value.trim()) return store.archiveListing.files
  const keyword = searchTerm.value.toLowerCase()
  return store.archiveListing.files.filter((file) => file.name.toLowerCase().includes(keyword))
})

function openArchiveImage(file: string) {
  const baseIndex = store.archiveListing?.files.findIndex((item) => item.path === file) ?? 0
  router.push({ path: '/image', query: { archive, file, index: String(baseIndex) } })
}

function goBack() {
  router.push('/')
}

function loadMore() {
  if (!store.archiveListing) return
  store.loadArchive(archive, store.archiveListing.page + 1, store.archiveListing.page_size, true)
}

function thumb(filePath: string) {
  return archiveThumbUrl(archive, filePath)
}
</script>

<style scoped>
.top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.title {
  font-weight: 700;
  font-family: 'Space Grotesk', Arial, sans-serif;
}

.subtitle {
  font-size: 12px;
  color: var(--muted);
}

.panel {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--stroke);
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0 12px 24px rgba(20, 25, 35, 0.08);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 12px;
}

.panel-title {
  font-size: 18px;
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-weight: 700;
}

.panel-sub {
  font-size: 12px;
  color: var(--muted);
}

.meta {
  font-size: 12px;
  color: var(--muted);
}

.ghost {
  background: transparent;
  border: 1px solid var(--stroke);
  border-radius: 999px;
  padding: 6px 14px;
  cursor: pointer;
}

.primary {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 10px 18px;
  cursor: pointer;
  font-weight: 600;
}

.load {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

.error {
  color: #b00020;
  margin-top: 12px;
}

.loading {
  margin-top: 8px;
  color: var(--muted);
}

.search {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.search input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  background: #fff;
  font-size: 14px;
}

.count {
  font-size: 12px;
  color: var(--muted);
}
</style>
