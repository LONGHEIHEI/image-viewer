<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">集合</div>
      <div class="page-actions">
        <n-button type="primary" @click="openCreate">新增集合</n-button>
      </div>
    </div>

    <n-card class="panel" :bordered="false">
      <div class="collections-grid">
        <div v-for="item in collections" :key="item.id" class="collection-card">
          <div class="cover">
            <img
              :src="collectionCoverUrl(item.id)"
              :alt="item.name"
              loading="lazy"
              @error="onCoverError"
            />
            <div class="cover-fallback">图集封面</div>
            <div class="cover-sheen"></div>
          </div>
          <div class="card-body">
            <div class="title">{{ item.name }}</div>
            <div class="subtitle">{{ item.paths.join(', ') }}</div>
          </div>
          <div class="card-actions">
            <n-button size="small" @click="openEdit(item)">编辑</n-button>
            <n-popconfirm @positive-click="remove(item.id)" positive-text="删除" negative-text="取消">
              <template #trigger>
                <n-button size="small" type="error">删除</n-button>
              </template>
              确认删除该集合？
            </n-popconfirm>
          </div>
        </div>
      </div>
      <div v-if="!collections.length" class="empty">暂无集合</div>

      <div v-if="error" class="error">{{ error }}</div>
    </n-card>

    <n-modal
      v-model:show="showCreate"
      title="新增集合"
      :style="{ width: 'min(600px, 92vw)' }"
      :transition-name="null"
      :mask-transition-name="null"
    >
      <div class="flat-form modal-surface">
        <n-form-item label="显示名称">
          <n-input v-model:value="newCollection.name" placeholder="请输入显示名称" />
        </n-form-item>
        <n-form-item label="文件夹">
          <div class="folder-block">
            <n-list bordered class="path-list">
              <n-list-item v-for="path in newCollection.paths" :key="path">
                <div class="row">
                  <div class="path-pill">{{ path }}</div>
                  <n-button size="tiny" @click="removePath(path, 'create')">移除</n-button>
                </div>
              </n-list-item>
              <n-list-item v-if="!newCollection.paths.length">
                <div class="empty">未添加任何文件夹</div>
              </n-list-item>
            </n-list>
            <n-button size="small" @click="openPicker('create')">添加</n-button>
          </div>
        </n-form-item>
        <n-form-item label="封面图">
          <n-input
            v-model:value="newCollection.cover_path"
            placeholder="可选，留空则自动选择并固定"
          />
        </n-form-item>
        <n-form-item label="访问密码">
          <n-input v-model:value="newCollection.password" type="password" placeholder="可留空" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="newCollection.aggregate_subdirs">汇总子目录</n-checkbox>
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" @click="create">创建</n-button>
        </n-space>
      </div>
    </n-modal>

    <n-modal
      v-model:show="showEdit"
      title="编辑集合"
      :style="{ width: 'min(600px, 92vw)' }"
      :transition-name="null"
      :mask-transition-name="null"
    >
      <div class="flat-form modal-surface">
        <n-form-item label="显示名称">
          <n-input v-model:value="editForm.name" placeholder="请输入显示名称" />
        </n-form-item>
        <n-form-item label="文件夹">
          <div class="folder-block">
            <n-list bordered class="path-list">
              <n-list-item v-for="path in editForm.paths" :key="path">
                <div class="row">
                  <div class="path-pill">{{ path }}</div>
                  <n-button size="tiny" @click="removePath(path, 'edit')">移除</n-button>
                </div>
              </n-list-item>
              <n-list-item v-if="!editForm.paths.length">
                <div class="empty">未添加任何文件夹</div>
              </n-list-item>
            </n-list>
            <n-button size="small" @click="openPicker('edit')">添加</n-button>
          </div>
        </n-form-item>
        <n-form-item label="封面图">
          <n-input
            v-model:value="editForm.cover_path"
            placeholder="可选，留空则自动选择并固定"
          />
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="editForm.password" type="password" placeholder="不修改请留空" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.clearPassword">清空密码</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.aggregate_subdirs">汇总子目录</n-checkbox>
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.clearCover">清空封面</n-checkbox>
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" @click="save">保存</n-button>
        </n-space>
      </div>
    </n-modal>

    <n-modal
      v-model:show="pickerVisible"
      title="选择路径"
      :style="{ width: 'min(780px, 96vw)' }"
      :transition-name="null"
      :mask-transition-name="null"
    >
      <div class="flat-form modal-surface picker">
        <div class="picker-tip">
          如果在列表里找不到你的设备，可以手动输入路径。例如：
          <span class="mono">\\\\server</span> 或 <span class="mono">\\\\192.168.1.10</span>。
        </div>
        <div class="picker-input">
          <n-input v-model:value="manualPath" placeholder="手动输入路径" clearable />
          <n-button size="small" type="primary" @click="addManualPath">添加</n-button>
        </div>
        <div class="picker-header">
          <div class="picker-path">{{ pickerPath || '根目录' }}</div>
          <n-space size="small">
            <n-button size="small" @click="goUp" :disabled="pickerLoading">上一级</n-button>
            <n-button size="small" type="primary" @click="addCurrent" :disabled="!pickerPath">
              添加当前目录
            </n-button>
          </n-space>
        </div>
        <div class="picker-search">
          <n-input v-model:value="pickerSearch" placeholder="搜索目录" clearable />
          <span class="count">已显示 {{ filteredPickerFolders.length }} 个</span>
        </div>
        <n-list bordered class="picker-list">
          <n-list-item v-for="folder in filteredPickerFolders" :key="folder.path">
            <div class="row picker-row" @click="enterFolder(folder.path)">
              <div class="picker-name">
                <div class="picker-title">{{ folder.name }}</div>
                <div class="picker-sub">{{ folder.path }}</div>
              </div>
              <n-button size="tiny" type="primary" @click.stop="addSelected(folder.path)">
                选择
              </n-button>
            </div>
          </n-list-item>
          <n-list-item v-if="!filteredPickerFolders.length && !pickerLoading">
            <div class="empty">没有匹配的目录</div>
          </n-list-item>
        </n-list>
        <div class="picker-status">
          <span v-show="pickerLoading" class="loading">加载中...</span>
          <span v-show="pickerError" class="error">{{ pickerError }}</span>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NCard,
  NButton,
  NList,
  NListItem,
  NInput,
  NModal,
  NFormItem,
  NSpace,
  NPopconfirm,
  NCheckbox,
  useNotification
} from 'naive-ui'
import {
  getCollectionsAdmin,
  createCollection,
  updateCollection,
  deleteCollection,
  getFsRoots,
  listFs,
  collectionCoverUrl,
  type CollectionAdmin,
  type FolderItem
} from '../api/client'

const collections = ref<CollectionAdmin[]>([])
const error = ref('')
const notification = useNotification()

const showCreate = ref(false)
const showEdit = ref(false)
const pickerVisible = ref(false)
const pickerLoading = ref(false)
const pickerError = ref('')
const pickerPath = ref('')
const pickerParent = ref('')
const pickerFolders = ref<FolderItem[]>([])
const pickerTarget = ref<'create' | 'edit'>('create')
const pickerSearch = ref('')
const manualPath = ref('')

const newCollection = ref({
  name: '',
  paths: [] as string[],
  password: '',
  cover_path: '',
  aggregate_subdirs: false
})

const editing = ref<CollectionAdmin | null>(null)
const editForm = ref({
  name: '',
  paths: [] as string[],
  password: '',
  clearPassword: false,
  cover_path: '',
  clearCover: false,
  aggregate_subdirs: false
})

const filteredPickerFolders = computed(() => {
  const keyword = pickerSearch.value.trim().toLowerCase()
  if (!keyword) return pickerFolders.value
  return pickerFolders.value.filter(
    (folder) =>
      folder.name.toLowerCase().includes(keyword) ||
      folder.path.toLowerCase().includes(keyword)
  )
})

onMounted(() => {
  load()
})

function normalizePathInput(path: string) {
  return path.replace(/\\/g, '/').trim()
}

function getTargetPaths() {
  return pickerTarget.value === 'create' ? newCollection.value.paths : editForm.value.paths
}

function setTargetPaths(paths: string[]) {
  if (pickerTarget.value === 'create') {
    newCollection.value.paths = paths
  } else {
    editForm.value.paths = paths
  }
}

function appendPath(path: string) {
  const normalized = normalizePathInput(path)
  if (!normalized) return
  const existing = getTargetPaths()
  if (!existing.includes(normalized)) {
    setTargetPaths([...existing, normalized])
  }
}

function removePath(path: string, target: 'create' | 'edit') {
  if (target === 'create') {
    newCollection.value.paths = newCollection.value.paths.filter((item) => item !== path)
    return
  }
  editForm.value.paths = editForm.value.paths.filter((item) => item !== path)
}

async function openPicker(target: 'create' | 'edit') {
  pickerTarget.value = target
  pickerSearch.value = ''
  manualPath.value = ''
  pickerVisible.value = true
  await loadRoots()
}

async function loadRoots() {
  pickerLoading.value = true
  pickerError.value = ''
  try {
    const roots = await getFsRoots()
    pickerFolders.value = roots.map((root) => ({ name: root.name, path: root.path }))
    pickerPath.value = ''
    pickerParent.value = ''
  } catch (err) {
    pickerError.value = err instanceof Error ? err.message : '加载失败'
    notification.error({ title: '加载失败', content: pickerError.value })
  } finally {
    pickerLoading.value = false
  }
}

async function enterFolder(path: string) {
  pickerLoading.value = true
  pickerError.value = ''
  try {
    const data = await listFs(path)
    pickerPath.value = data.path
    pickerParent.value = data.parent
    pickerFolders.value = data.folders
  } catch (err) {
    pickerError.value = err instanceof Error ? err.message : '加载失败'
    notification.error({ title: '加载失败', content: pickerError.value })
  } finally {
    pickerLoading.value = false
  }
}

async function goUp() {
  if (!pickerParent.value) {
    await loadRoots()
    return
  }
  await enterFolder(pickerParent.value)
}

function addCurrent() {
  if (!pickerPath.value) return
  appendPath(pickerPath.value)
}

function addSelected(path: string) {
  appendPath(path)
}

function addManualPath() {
  if (!manualPath.value.trim()) return
  appendPath(manualPath.value)
  manualPath.value = ''
}

async function load() {
  error.value = ''
  try {
    collections.value = await getCollectionsAdmin()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    notification.error({ title: '加载失败', content: error.value })
  }
}

function openCreate() {
  newCollection.value = {
    name: '',
    paths: [],
    password: '',
    cover_path: '',
    aggregate_subdirs: false
  }
  showCreate.value = true
}

async function create() {
  error.value = ''
  try {
    await createCollection({
      name: newCollection.value.name,
      paths: newCollection.value.paths,
      password: newCollection.value.password || undefined,
      cover_path: newCollection.value.cover_path || undefined,
      aggregate_subdirs: newCollection.value.aggregate_subdirs
    })
    showCreate.value = false
    notification.success({ title: '创建成功', content: `集合 ${newCollection.value.name} 已创建` })
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建失败'
    notification.error({ title: '创建失败', content: error.value })
  }
}

function openEdit(item: CollectionAdmin) {
  editing.value = item
  editForm.value = {
    name: item.name,
    paths: [...item.paths],
    password: '',
    clearPassword: false,
    cover_path: item.cover_path || '',
    clearCover: false,
    aggregate_subdirs: item.aggregate_subdirs
  }
  showEdit.value = true
}

async function save() {
  if (!editing.value) return
  error.value = ''
  try {
    await updateCollection(editing.value.id, {
      name: editForm.value.name,
      paths: editForm.value.paths,
      password: editForm.value.password || undefined,
      clear_password: editForm.value.clearPassword,
      cover_path: editForm.value.cover_path || undefined,
      clear_cover: editForm.value.clearCover,
      aggregate_subdirs: editForm.value.aggregate_subdirs
    })
    showEdit.value = false
    notification.success({ title: '更新成功', content: `已更新集合 ${editForm.value.name}` })
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新失败'
    notification.error({ title: '更新失败', content: error.value })
  }
}

async function remove(id: number) {
  error.value = ''
  try {
    await deleteCollection(id)
    notification.success({ title: '删除成功', content: '集合已删除' })
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '删除失败'
    notification.error({ title: '删除失败', content: error.value })
  }
}

function onCoverError(event: Event) {
  const target = event.target as HTMLImageElement | null
  if (!target) return
  target.classList.add('hidden')
}
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  border: 1px solid var(--stroke);
  border-radius: 12px;
  overflow: hidden;
  background: #f7f7f7;
  flex: 0 0 auto;
  position: relative;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover img.hidden {
  display: none;
}

.cover-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-2);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background:
    radial-gradient(circle at 20% 20%, rgba(170, 196, 255, 0.35), transparent 42%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(240, 244, 248, 0.95));
}

.cover img:not(.hidden) ~ .cover-fallback {
  opacity: 0;
}

.cover-sheen {
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0));
  pointer-events: none;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.collection-card {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(27, 30, 39, 0.08);
  border-radius: 14px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(20, 25, 35, 0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.collection-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 16px 30px rgba(20, 25, 35, 0.12);
}

.card-body {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.title {
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subtitle {
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.name {
  font-weight: 700;
}

.folder-block {
  display: grid;
  gap: 6px;
  width: 100%;
}

.path-list :deep(.n-list) {
  border: 1px solid var(--stroke);
  border-radius: 8px;
  background: transparent;
}

.path-list :deep(.n-list-item) {
  padding: 6px 8px;
  border-radius: 0;
  border: none;
  background: transparent;
}

.path-pill {
  padding: 2px 6px;
  border-radius: 4px;
  background: transparent;
  border: 1px solid var(--stroke);
  color: var(--ink);
  font-size: 11px;
  word-break: break-all;
}

.picker {
  display: grid;
  gap: 8px;
}

.picker-tip {
  font-size: 11px;
  color: var(--muted);
  padding: 0;
}

.mono {
  font-family: 'Space Grotesk', 'Archivo', Arial, sans-serif;
}

.picker-input {
  display: grid;
  gap: 6px;
  grid-template-columns: 1fr auto;
  align-items: center;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

.picker-path {
  flex: 1;
  min-width: 0;
  font-size: 11px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.picker-search {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.picker-list {
  height: 320px;
  max-height: 320px;
  min-height: 320px;
  overflow-y: scroll;
  overflow-x: hidden;
  scrollbar-gutter: stable;
}

.picker-list :deep(.n-list-item) {
  padding: 8px 10px;
  border-radius: 0;
  border: none;
  background: transparent;
  margin-bottom: 0;
}

.picker-row {
  cursor: pointer;
}

.picker-row:hover .picker-title {
  text-decoration: underline;
}

.picker-status {
  min-height: 18px;
  font-size: 11px;
}

.picker-name {
  display: grid;
  gap: 2px;
}

.picker-title {
  font-weight: 600;
  font-size: 12px;
}

.picker-sub {
  font-size: 11px;
  color: var(--muted);
  word-break: break-all;
}

.flat-form {
  display: grid;
  gap: 10px;
  padding: 6px 2px 2px;
}

.flat-form :deep(.n-form-item) {
  margin: 0;
}

.flat-form :deep(.n-form-item-label) {
  font-size: 12px;
  font-weight: 600;
  padding-bottom: 2px;
}

.flat-form :deep(.n-form-item-blank) {
  margin-top: 2px;
}

.flat-form :deep(.n-card-header),
.flat-form :deep(.n-card__content) {
  padding: 0;
}

.flat-form :deep(.n-list) {
  border: 1px solid var(--stroke);
  border-radius: 8px;
  background: transparent;
}

.flat-form :deep(.n-list-item) {
  padding: 6px 8px;
  border-radius: 0;
  border: none;
  background: transparent;
}

.modal-surface {
  background: #fff;
  border: 1px solid var(--stroke);
  border-radius: 10px;
  padding: 10px 12px;
  box-shadow: none;
}

@media (max-width: 960px) {
  .row {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .collections-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
  }

  .card-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .card-actions > * {
    flex: 1 1 120px;
  }

  .picker-input {
    grid-template-columns: 1fr;
  }

  .picker-list {
    height: min(320px, 48vh);
    max-height: min(320px, 48vh);
    min-height: 220px;
  }

  .picker-search {
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }

  .collection-card {
    padding: 10px;
  }

  .picker-header {
    align-items: flex-start;
  }

  .picker-header :deep(.n-space) {
    width: 100%;
  }
}
</style>
