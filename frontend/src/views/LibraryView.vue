<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title-area">
        <div class="title-row">
          <n-button
            v-if="store.currentFolder"
            class="back-btn"
            quaternary
            size="small"
            @click="openFolder(getParentPath())"
          >
            <template #icon>
              <svg viewBox="0 0 24 24" width="16" height="16"><path d="M15 6l-6 6l6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </template>
            返回上级
          </n-button>
          <Breadcrumbs
            v-if="store.currentFolder"
            class="page-crumbs"
            :path="store.currentFolder"
            root-label="全部"
            @navigate="openFolder"
          />
        </div>
      </div>
    </div>

    <section v-if="store.listing && (store.listing.folders.length || store.listing.archives.length)" class="folder-section">
      <div class="section-label">目录</div>
      <FolderGrid
        :folders="store.listing.folders"
        :archives="store.listing.archives"
        :folder-thumb="folderThumb"
        :archive-thumb="archiveThumb"
        @open-folder="openFolder"
        @open-archive="openArchive"
      />
    </section>

    <section
      v-if="store.listing && store.listing.total_images"
      class="image-section"
    >
      <ImageBrowserSection
        :images="store.listing.images"
        :thumb="thumb"
        title="图片"
        :meta-text="`共 ${store.listing.total_images} 张 · 第 ${store.listing.page} 页`"
        :has-more="store.listing.has_more"
        :loading="store.loading"
        favorite-enabled
        :is-favorite="isFavorite"
        :toggle-favorite="toggleFavorite"
        @open-image="openImage"
        @load-more="loadMore"
      />
    </section>

    <div v-if="store.loading && !store.listing" class="loading">加载中...</div>
    <div v-if="store.error" class="error">{{ store.error }}</div>

    <div
      v-if="store.listing && !store.listing.folders.length && !store.listing.archives.length && !store.listing.total_images && !store.loading"
      class="empty-folder"
    >
      <div class="empty-folder-icon">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <div class="empty-folder-title">此目录为空</div>
      <div class="empty-folder-desc">该目录下暂无图片或子目录</div>
      <n-button v-if="store.currentFolder" quaternary size="small" @click="openFolder(getParentPath())">
        <template #icon>
          <svg viewBox="0 0 24 24" width="16" height="16"><path d="M15 6l-6 6l6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </template>
        返回上级
      </n-button>
    </div>

    <div
      v-if="!store.listing && !store.loading && !store.error"
      class="empty-folder"
    >
      <div class="empty-folder-icon">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <path d="m21 15l-5-5L5 21"/>
        </svg>
      </div>
      <div class="empty-folder-title">欢迎使用轻图</div>
      <div class="empty-folder-desc">将图片放入 photos 目录即可开始浏览</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGalleryStore } from '../store/gallery'
import { NButton } from 'naive-ui'
import FolderGrid from '../components/FolderGrid.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import ImageBrowserSection from '../components/ImageBrowserSection.vue'
import { folderCoverUrl, archiveCoverUrl, thumbUrl } from '../api/client'
import { buildFavoriteKey } from '../utils/favorites'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  store.loadTree(3)
})

watch(
  () => String(route.query.path || ''),
  (path) => {
    store.loadFolder(path)
  },
  { immediate: true }
)

function openFolder(path: string) {
  router.push({
    path: '/library',
    query: path ? { path } : {}
  })
}

function getParentPath(): string {
  const path = store.currentFolder || ''
  return path.split('/').slice(0, -1).join('/')
}

function openArchive(path: string) {
  const query: Record<string, string> = { archive: path }
  const currentPath = String(route.query.path || '')
  if (currentPath) {
    query.folder = currentPath
  }
  router.push({ path: '/folder', query })
}

function openImage(path: string) {
  const folder = store.currentFolder
  const baseIndex = store.listing?.images.findIndex((img) => img.path === path) ?? 0
  router.push({ path: '/image', query: { path, index: String(baseIndex), folder } })
}

function favoritePayload(path: string) {
  const item = store.listing?.images.find((image) => image.path === path)
  return {
    source_kind: 'image' as const,
    item_path: path,
    folder_path: store.currentFolder,
    view_mode: 'folder' as const,
    item_name: item?.name || path.split(/[\\/]+/).filter(Boolean).pop() || path
  }
}

function isFavorite(path: string) {
  return store.hasFavorite(buildFavoriteKey(favoritePayload(path)))
}

async function toggleFavorite(path: string) {
  await store.toggleFavorite(favoritePayload(path))
}

function loadMore() {
  if (!store.listing) return
  store.loadFolder(store.currentFolder, store.listing.page + 1, store.listing.page_size, true)
}

function thumb(path: string) {
  return thumbUrl(path)
}

function folderThumb(path: string) {
  return folderCoverUrl(path)
}

function archiveThumb(path: string) {
  return archiveCoverUrl(path)
}
</script>

<style scoped>
.page {
  gap: 20px;
}

.page-header {
  align-items: center;
}

.page-title-area {
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.back-btn {
  flex-shrink: 0;
}

.page-crumbs {
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 0;
  flex-wrap: wrap;
}

.folder-section {
  display: grid;
  gap: 10px;
}

.image-section {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.section-label {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 13px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding-left: 2px;
}

.empty-folder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 64px 24px;
  text-align: center;
  min-width: 0;
}

.empty-folder-icon {
  color: rgba(92, 102, 114, 0.3);
  margin-bottom: 4px;
}

.empty-folder-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--ink);
}

.empty-folder-desc {
  font-size: 13px;
  color: var(--muted);
  max-width: 280px;
}

@media (max-width: 960px) {
  .page {
    gap: 16px;
  }

  .title-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .page-crumbs {
    font-size: 12px;
  }

  .empty-folder {
    padding: 48px 20px;
  }
}
</style>
