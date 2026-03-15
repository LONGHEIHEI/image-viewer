<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">图库</div>
    </div>

    <n-layout has-sider class="layout">
      <n-layout-sider width="280" class="left" collapse-mode="width" :collapsed-width="0">
        <SidebarTree
          :tree="store.tree"
          :loading="store.treeLoading"
          :error="store.treeError"
          @open-folder="openFolder"
          @open-archive="openArchive"
          @refresh="refreshTree"
        />
      </n-layout-sider>

      <n-layout-content class="main">
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
            <n-button size="small" @click="refresh">刷新</n-button>
          </div>
          <FolderGrid
            v-if="store.listing"
            :folders="store.listing.folders"
            :archives="store.listing.archives"
            :folder-thumb="folderThumb"
            @open-folder="openFolder"
            @open-archive="openArchive"
          />
        </n-card>

        <div v-if="store.error" class="error">{{ store.error }}</div>
        <div v-if="store.loading" class="loading">加载中...</div>
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NLayout, NLayoutSider, NLayoutContent, NCard, NButton } from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import FolderGrid from '../components/FolderGrid.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import SidebarTree from '../components/SidebarTree.vue'
import { folderCoverUrl } from '../api/client'

const store = useGalleryStore()
const router = useRouter()

onMounted(() => {
  store.loadFolder('')
  store.loadTree(3)
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

function folderThumb(path: string) {
  return folderCoverUrl(path)
}
</script>

<style scoped>
.layout {
  background: transparent;
  gap: 12px;
  align-items: flex-start;
}

.left {
  background: transparent;
  padding-right: 4px;
}

.main {
  background: transparent;
  display: grid;
  gap: 16px;
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
    display: block;
  }

  .left {
    padding-right: 0;
  }
}
</style>
