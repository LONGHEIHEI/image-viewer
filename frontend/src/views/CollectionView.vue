<template>
  <div class="page">
    <div class="page-header page-header--actions-only page-header--mobile-hidden">
      <div class="page-actions">
        <span v-if="store.collectionListing?.total_images" class="page-meta-badge">
          共 {{ store.collectionListing.total_images }} 张
        </span>
        <n-button size="small" @click="goBack">返回</n-button>
      </div>
    </div>

    <div v-if="showPrivacyToggleButton" class="privacy-toolbar">
      <PrivacyRevealButton
        :title="privacyToggleTitle"
        :active="allCurrentRevealed"
        @click="toggleCurrentFolderPrivacy"
      />
    </div>

    <section class="collection-section">
      <FolderGrid
        v-if="store.collectionListing"
        :folders="store.collectionListing.folders"
        :archives="store.collectionListing.archives"
        :folder-thumb="folderThumb"
        :archive-thumb="archiveThumb"
        :card-min-width="260"
        :privacy-enabled="privacyEnabled"
        :privacy-storage-key="privacyStorageKey"
        @open-folder="openFolder"
        @open-archive="openArchive"
      />
    </section>

    <div
      class="collection-section image-panel"
      v-if="
        store.collectionListing &&
        (
          store.collectionListing.images.length > 0 ||
          store.collectionListing.total_images > 0 ||
          store.collectionListing.has_more
        )
      "
    >
      <ImageGrid
        v-if="store.collectionListing.images.length"
        :images="store.collectionListing.images"
        :thumb="thumb"
        :privacy-enabled="privacyEnabled"
        :privacy-storage-key="privacyStorageKey"
        @open-image="openImage"
      />
      <div class="load" v-if="store.collectionListing.has_more">
        <n-button type="primary" :loading="store.loading" @click="loadMore">加载更多</n-button>
      </div>
    </div>

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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NInput,
  NModal,
  NForm,
  NFormItem,
  NSpace,
  useNotification
} from 'naive-ui'
import { useGalleryStore } from '../store/gallery'
import FolderGrid from '../components/FolderGrid.vue'
import ImageGrid from '../components/ImageGrid.vue'
import PrivacyRevealButton from '../components/PrivacyRevealButton.vue'
import { usePrivacyReveal } from '../composables/usePrivacyReveal'
import {
  accessCollection,
  collectionThumbUrl,
  collectionArchiveCoverUrl,
  collectionFolderCoverUrl,
  getCollectionInfo,
  setCollectionToken
} from '../api/client'

const store = useGalleryStore()
const route = useRoute()
const router = useRouter()
const notification = useNotification()

const collectionId = computed(() => Number(route.params.id))
const collectionPath = computed(() => String(route.query.path || ''))
const collectionName = ref('图集')
const requiresPassword = ref(false)
const privacyEnabled = ref(false)
const showPassword = ref(false)
const password = ref('')
const flatMode = ref(false)
const privacyStorageKey = computed(() => `collection-privacy-${collectionId.value}`)
const { isRevealed, revealMany, hideMany, reset } = usePrivacyReveal(privacyStorageKey)
// When user taps "show current folder", we keep auto-revealing newly appended items
// (e.g. via "load more") until they explicitly hide again. Reset on folder/view change.
const autoRevealCurrentFolder = ref(false)

const currentPrivacyKeys = computed(() => {
  const listing = store.collectionListing
  if (!listing || !privacyEnabled.value) {
    return [] as string[]
  }
  return [
    ...listing.folders.map((folder) => `folder:${folder.path}`),
    ...listing.archives.map((archive) => `archive:${archive.path}`),
    ...listing.images.map((image) => `image:${image.path}`)
  ]
})

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

watch(
  () => `${String(route.params.id || '')}|${String(route.query.path || '')}|${String(route.query.view || '')}|${String(route.query.privacy || '')}`,
  async () => {
    autoRevealCurrentFolder.value = false
    reset()
    await loadCollection()
  },
  { immediate: true }
)

watch(
  () => currentPrivacyKeys.value.length,
  () => {
    if (!autoRevealCurrentFolder.value) return
    // Idempotent: revealMany returns false when nothing changed.
    revealMany(currentPrivacyKeys.value)
  }
)

async function loadCollection() {
  try {
    const info = await getCollectionInfo(collectionId.value)
    collectionName.value = info.name
    store.collectionName = info.name
    store.collectionPrivacyEnabled = Boolean(info.privacy_enabled)
    requiresPassword.value = info.requires_password
    privacyEnabled.value = Boolean(info.privacy_enabled)
    if (privacyEnabled.value) {
      // Entering a privacy-enabled collection should always start masked,
      // regardless of the previous reveal state in this session.
      reset()
    }
    flatMode.value = resolveInitialView(info.aggregate_subdirs)
    const existingToken = localStorage.getItem(`collection_token_${collectionId.value}`)
    if (requiresPassword.value && !existingToken) {
      showPassword.value = true
      return
    }
    await store.loadCollectionFolder(
      collectionId.value,
      collectionPath.value,
      1,
      20,
      false,
      flatMode.value ? 'flat' : 'folder'
    )
  } catch (err) {
    notification.error({ title: '加载失败', content: err instanceof Error ? err.message : '加载失败' })
    router.push('/collections')
  }
}

function resolveInitialView(aggregateSubdirs?: boolean) {
  if (route.query.view === 'flat') return true
  if (route.query.view === 'folder') return false
  return Boolean(aggregateSubdirs)
}

async function confirmPassword() {
  try {
    const result = await accessCollection(collectionId.value, password.value)
    setCollectionToken(collectionId.value, result.token || '')
    showPassword.value = false
    await store.loadCollectionFolder(
      collectionId.value,
      collectionPath.value,
      1,
      20,
      false,
      flatMode.value ? 'flat' : 'folder'
    )
  } catch (err) {
    notification.error({ title: '密码错误', content: err instanceof Error ? err.message : '密码错误' })
  }
}

function buildCollectionRoute(path: string) {
  const query: Record<string, string> = {}
  if (path) {
    query.path = path
  }
  if (flatMode.value) {
    query.view = 'flat'
  }
  if (privacyEnabled.value) {
    query.privacy = '1'
  }
  return {
    path: `/collection/${collectionId.value}`,
    query
  }
}

function openFolder(path: string) {
  router.push(buildCollectionRoute(path))
}

function openArchive(path: string) {
  const query: Record<string, string> = {
    archive: path,
    collection: String(collectionId.value),
    view: flatMode.value ? 'flat' : 'folder'
  }
  if (collectionPath.value) {
    query.folder = collectionPath.value
  }
  if (privacyEnabled.value) {
    query.privacy = '1'
  }
  router.push({
    path: '/folder',
    query
  })
}

function openImage(path: string) {
  const baseIndex = store.collectionListing?.images.findIndex((img) => img.path === path) ?? 0
  router.push({
    path: '/image',
    query: {
      path,
      index: String(baseIndex),
      folder: collectionPath.value,
      collection: String(collectionId.value),
      view: flatMode.value ? 'flat' : 'folder',
      ...(privacyEnabled.value ? { privacy: '1' } : {})
    }
  })
}

function loadMore() {
  if (!store.collectionListing) return
  store.loadCollectionFolder(
    collectionId.value,
    collectionPath.value,
    store.collectionListing.page + 1,
    store.collectionListing.page_size,
    true,
    flatMode.value ? 'flat' : 'folder'
  )
}

function toggleCurrentFolderPrivacy() {
  if (allCurrentRevealed.value) {
    autoRevealCurrentFolder.value = false
    hideMany(currentPrivacyKeys.value)
    return
  }
  autoRevealCurrentFolder.value = true
  revealMany(currentPrivacyKeys.value)
}

function thumb(path: string) {
  return collectionThumbUrl(collectionId.value, path)
}

function folderThumb(path: string) {
  return collectionFolderCoverUrl(collectionId.value, path)
}

function archiveThumb(path: string) {
  return collectionArchiveCoverUrl(collectionId.value, path)
}

function goBack() {
  router.push('/collections')
}
</script>

<style scoped>
.modal {
  width: min(420px, 92vw);
}

.page-header--actions-only {
  justify-content: flex-end;
}

.collection-section {
  display: grid;
  gap: 12px;
}

.privacy-toolbar {
  position: fixed;
  right: calc(20px + env(safe-area-inset-right));
  bottom: calc(22px + env(safe-area-inset-bottom));
  z-index: 40;
}

.image-panel {
  padding-top: 0;
}

@media (max-width: 960px) {
  .page-header--mobile-hidden {
    display: none;
  }

  .page-header--actions-only {
    justify-content: flex-start;
  }

  .collection-section {
    gap: 10px;
  }

  .privacy-toolbar {
    right: calc(14px + env(safe-area-inset-right));
    bottom: calc(16px + env(safe-area-inset-bottom));
  }

  .image-panel {
    padding-top: 0;
  }
}
</style>
