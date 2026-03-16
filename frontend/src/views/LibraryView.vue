<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">图库</div>
    </div>

    <div class="layout">
      <section class="left">
        <SidebarTree
          :tree="store.tree"
          :loading="store.treeLoading"
          :error="store.treeError"
          @open-folder="openFolder"
          @open-archive="openArchive"
        />
      </section>

      <div class="main">
        <n-card class="panel" :bordered="false">
          <div class="panel-header">
            <div class="panel-left">
              <div class="panel-title">目录</div>
              <Breadcrumbs
                class="panel-crumbs"
                :path="store.currentFolder"
                compact
                @navigate="openFolder"
              />
            </div>
          </div>
          <FolderGrid
            v-if="store.listing"
            :folders="store.listing.folders"
            :archives="store.listing.archives"
            :folder-thumb="folderThumb"
            :archive-thumb="archiveThumb"
            @open-folder="openFolder"
            @open-archive="openArchive"
          />
        </n-card>

        <n-card
          v-if="store.listing && store.listing.total_images"
          class="panel"
          :bordered="false"
        >
          <div class="panel-header">
            <div class="panel-title">图片</div>
            <div class="meta">
              共 {{ store.listing.total_images }} 张 · 第 {{ store.listing.page }} 页
            </div>
          </div>
          <ImageGrid :images="store.listing.images" :thumb="thumb" @open-image="openImage" />
          <div class="load" v-if="store.listing.has_more">
            <n-button type="primary" :loading="store.loading" @click="loadMore">加载更多</n-button>
          </div>
        </n-card>

        <div v-if="store.error" class="error">{{ store.error }}</div>
        <div v-if="store.loading" class="loading">加载中...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NButton } from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import FolderGrid from '../components/FolderGrid.vue'
import ImageGrid from '../components/ImageGrid.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import SidebarTree from '../components/SidebarTree.vue'
import { folderCoverUrl, archiveCoverUrl, thumbUrl } from '../api/client'

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
    path: '/',
    query: path ? { path } : {}
  })
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
.layout {
  display: grid;
  grid-template-columns: minmax(240px, 280px) minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.left {
  min-width: 0;
}

.main {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.panel-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.panel-crumbs {
  margin: 0;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .left {
    order: 1;
  }

  .panel-left {
    align-items: flex-start;
    gap: 8px;
  }

  .panel-crumbs {
    width: 100%;
  }
}
</style>
