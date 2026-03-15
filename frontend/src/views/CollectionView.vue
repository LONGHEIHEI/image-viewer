<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">集合：{{ collectionName }}</div>
      <div class="page-actions">
        <n-button size="small" @click="goBack">返回</n-button>
        <n-button size="small" @click="refresh">刷新</n-button>
      </div>
    </div>

    <n-card class="panel" :bordered="false">
      <Breadcrumbs :path="store.collectionFolder" :root-label="collectionName" @navigate="openFolder" />
      <FolderGrid
        v-if="store.collectionListing"
        :folders="store.collectionListing.folders"
        :archives="store.collectionListing.archives"
        :folder-thumb="folderThumb"
        @open-folder="openFolder"
        @open-archive="openArchive"
      />
    </n-card>

    <n-card class="panel" v-if="store.collectionListing" :bordered="false">
      <div class="panel-header">
        <div class="panel-title">图片</div>
        <div class="meta" v-if="store.collectionListing.total_images">
          共 {{ store.collectionListing.total_images }} 张 · 第 {{ store.collectionListing.page }} 页
        </div>
      </div>
      <div class="search">
        <n-input v-model:value="searchTerm" placeholder="按名称搜索图片" clearable />
        <span class="count">已显示 {{ filteredImages.length }} 张</span>
      </div>
      <ImageGrid
        v-if="filteredImages.length"
        :images="filteredImages"
        :thumb="thumb"
        @open-image="openImage"
      />
      <div v-else class="empty">未找到图片。</div>
      <div class="load" v-if="store.collectionListing.has_more">
        <n-button type="primary" :loading="store.loading" @click="loadMore">加载更多</n-button>
      </div>
    </n-card>

    <div v-if="store.error" class="error">{{ store.error }}</div>
    <div v-if="store.loading" class="loading">加载中...</div>

    <n-modal v-model:show="showPassword" preset="card" title="集合访问" class="modal">
      <n-form>
        <n-form-item label="访问密码">
          <n-input v-model:value="password" type="password" placeholder="请输入集合密码" />
        </n-form-item>
        <n-space justify="end">
          <n-button @click="goBack">取消</n-button>
          <n-button type="primary" @click="confirmPassword">进入</n-button>
        </n-space>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NCard, NButton, NInput, NModal, NForm, NFormItem, NSpace, useNotification } from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import FolderGrid from '../components/FolderGrid.vue'
import ImageGrid from '../components/ImageGrid.vue'
import Breadcrumbs from '../components/Breadcrumbs.vue'
import {
  accessCollection,
  collectionThumbUrl,
  collectionFolderCoverUrl,
  getCollectionInfo,
  setCollectionToken
} from '../api/client'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()
const notification = useNotification()

const collectionId = Number(route.params.id)
const collectionName = ref('集合')
const requiresPassword = ref(false)
const showPassword = ref(false)
const password = ref('')
const searchTerm = ref('')

onMounted(async () => {
  await loadCollection()
})

const filteredImages = computed(() => {
  if (!store.collectionListing) return []
  if (!searchTerm.value.trim()) return store.collectionListing.images
  const keyword = searchTerm.value.toLowerCase()
  return store.collectionListing.images.filter((img) => img.name.toLowerCase().includes(keyword))
})

async function loadCollection() {
  try {
    const info = await getCollectionInfo(collectionId)
    collectionName.value = info.name
    requiresPassword.value = info.requires_password
    const existingToken = localStorage.getItem(`collection_token_${collectionId}`)
    if (requiresPassword.value && !existingToken) {
      showPassword.value = true
      return
    }
    await store.loadCollectionFolder(collectionId, '')
  } catch (err) {
    notification.error({ title: '加载失败', content: err instanceof Error ? err.message : '加载失败' })
    router.push('/')
  }
}

async function confirmPassword() {
  try {
    const result = await accessCollection(collectionId, password.value)
    setCollectionToken(collectionId, result.token || '')
    showPassword.value = false
    await store.loadCollectionFolder(collectionId, '')
  } catch (err) {
    notification.error({ title: '密码错误', content: err instanceof Error ? err.message : '密码错误' })
  }
}

function openFolder(path: string) {
  store.loadCollectionFolder(collectionId, path)
}

function refresh() {
  store.loadCollectionFolder(collectionId, store.collectionFolder)
}

function openArchive(path: string) {
  router.push({ path: '/folder', query: { archive: path, collection: String(collectionId) } })
}

function openImage(path: string) {
  const baseIndex = store.collectionListing?.images.findIndex((img) => img.path === path) ?? 0
  router.push({
    path: '/image',
    query: { path, index: String(baseIndex), folder: store.collectionFolder, collection: String(collectionId) }
  })
}

function loadMore() {
  if (!store.collectionListing) return
  store.loadCollectionFolder(
    collectionId,
    store.collectionFolder,
    store.collectionListing.page + 1,
    store.collectionListing.page_size,
    true
  )
}

function thumb(path: string) {
  return collectionThumbUrl(collectionId, path)
}

function folderThumb(path: string) {
  return collectionFolderCoverUrl(collectionId, path)
}

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.modal {
  width: min(420px, 92vw);
}
</style>
