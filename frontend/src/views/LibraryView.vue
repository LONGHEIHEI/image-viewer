<template>
  <div class="layout">
    <aside class="left">
      <SidebarTree
        :tree="store.tree"
        :loading="store.treeLoading"
        :error="store.treeError"
        @open-folder="openFolder"
        @open-archive="openArchive"
        @refresh="refreshTree"
      />
    </aside>

    <section class="main">
      <Breadcrumbs :path="store.currentFolder" @navigate="openFolder" />

      <div class="panel">
        <div class="panel-header">
          <div>
            <div class="panel-title">目录</div>
            <div class="panel-sub">浏览文件夹与压缩包</div>
          </div>
          <button class="ghost" @click="refresh">刷新</button>
        </div>
        <FolderGrid
          v-if="store.listing"
          :folders="store.listing.folders"
          :archives="store.listing.archives"
          @open-folder="openFolder"
          @open-archive="openArchive"
        />
      </div>

      <div class="panel" v-if="store.listing">
        <div class="panel-header">
          <div>
            <div class="panel-title">图片</div>
            <div class="panel-sub">{{ store.listing.total_images }} 张</div>
          </div>
          <div class="meta" v-if="store.listing.total_images">
            第 {{ store.listing.page }} 页
          </div>
        </div>
        <div class="search">
          <input v-model="searchTerm" placeholder="按名称搜索图片" />
          <span class="count">已显示 {{ filteredImages.length }} 张</span>
        </div>
        <ImageGrid
          v-if="filteredImages.length"
          :images="filteredImages"
          :thumb="thumb"
          @open-image="openImage"
        />
        <div v-else class="empty">未找到图片。</div>
        <div class="load" v-if="store.listing.has_more">
          <button class="primary" :disabled="store.loading" @click="loadMore">加载更多</button>
        </div>
      </div>

      <div v-if="store.error" class="error">{{ store.error }}</div>
      <div v-if="store.loading" class="loading">加载中...</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGalleryStore } from '../store/gallery'
import FolderGrid from '../components/FolderGrid.vue'
import ImageGrid from '../components/ImageGrid.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import SidebarTree from '../components/SidebarTree.vue'
import { thumbUrl } from '../api/client'

const store = useGalleryStore()
const router = useRouter()
const searchTerm = ref('')

onMounted(() => {
  store.loadFolder('')
  store.loadTree(3)
})

const filteredImages = computed(() => {
  if (!store.listing) return []
  if (!searchTerm.value.trim()) return store.listing.images
  const keyword = searchTerm.value.toLowerCase()
  return store.listing.images.filter((img) => img.name.toLowerCase().includes(keyword))
})

function openFolder(path: string) {
  store.loadFolder(path)
}

function refresh() {
  store.loadFolder(store.currentFolder)
}

function refreshTree() {
  store.loadTree(3)
}

function openArchive(path: string) {
  router.push({ path: '/folder', query: { archive: path } })
}

function openImage(path: string) {
  const folder = store.currentFolder
  const baseIndex = store.listing?.images.findIndex((img) => img.path === path) ?? 0
  router.push({ path: '/image', query: { path, index: String(baseIndex), folder } })
}

function loadMore() {
  if (!store.listing) return
  store.loadFolder(store.currentFolder, store.listing.page + 1, store.listing.page_size, true)
}

function thumb(path: string) {
  return thumbUrl(path)
}
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  align-items: start;
}

.left {
  position: sticky;
  top: 20px;
}

.panel {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--stroke);
  border-radius: 20px;
  padding: 18px;
  margin-bottom: 20px;
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

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.load {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

.meta {
  font-size: 12px;
  color: var(--muted);
}

.error {
  color: #b00020;
  margin-top: 12px;
}

.loading {
  margin-top: 8px;
  color: var(--muted);
}

.empty {
  padding: 16px 0;
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

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .left {
    position: static;
  }
}
</style>
