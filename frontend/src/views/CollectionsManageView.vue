<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">集合设置</div>
      <div class="page-actions">
        <n-button type="primary" size="small" @click="openCreate">新建图集</n-button>
      </div>
    </div>

    <div class="collections-grid" v-if="collections.length">
      <div v-for="item in collections" :key="item.id" class="collection-card">
        <div class="cover">
          <img
            :src="collectionCoverUrl(item.id)"
            :alt="item.name"
            loading="lazy"
            @error="onCoverError"
          />
          <div class="cover-fallback">图集封面</div>
        </div>
        <div class="card-body">
          <div class="title">{{ item.name }}</div>
          <div class="subtitle">{{ item.paths.length }} 个目录</div>
        </div>
        <div class="card-actions">
          <n-button size="small" quaternary @click="openEdit(item)">编辑</n-button>
          <n-popconfirm @positive-click="remove(item.id)" positive-text="删除" negative-text="取消">
            <template #trigger>
              <n-button size="small" quaternary type="error">删除</n-button>
            </template>
            确认删除该集合？
          </n-popconfirm>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <rect x="7" y="7" width="10" height="10" rx="1"/>
          <circle cx="12" cy="12" r="1.5"/>
        </svg>
      </div>
      <div class="empty-state-title">暂无图集</div>
      <div class="empty-state-desc">创建图集后，可将不同目录的图片聚合展示</div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <n-modal
      v-model:show="showCreate"
      title="新建图集"
      preset="card"
      :style="{ width: 'min(600px, 92vw)' }"
    >
      <n-form label-placement="top" :show-feedback="false">
        <n-form-item label="集合名称">
          <n-input v-model:value="newCollection.name" placeholder="用于前台展示" />
        </n-form-item>
        <n-form-item label="图片来源目录">
          <div class="path-block">
            <div class="path-list">
              <div v-for="path in newCollection.paths" :key="path" class="path-row">
                <span class="path-pill">{{ path }}</span>
                <n-button size="tiny" quaternary type="error" @click="removePath(path, 'create')">移除</n-button>
              </div>
              <div v-if="!newCollection.paths.length" class="path-empty">未添加目录</div>
            </div>
            <n-button size="small" quaternary @click="openPicker('create')">+ 添加目录</n-button>
          </div>
        </n-form-item>
        <n-form-item label="封面路径（可选）">
          <n-input v-model:value="newCollection.cover_path" placeholder="留空自动选择封面" />
        </n-form-item>
        <n-form-item label="访问密码（可选）">
          <n-input v-model:value="newCollection.password" type="password" placeholder="留空表示公开" />
        </n-form-item>
        <n-form-item label="确认密码">
          <n-input v-model:value="newCollection.confirmPassword" type="password" placeholder="再次输入" />
        </n-form-item>
        <div v-if="createPasswordMismatch" class="form-error">两次输入的密码不一致</div>
        <div class="check-list">
          <n-checkbox v-model:checked="newCollection.aggregate_subdirs">包含子目录（递归扫描）</n-checkbox>
          <n-checkbox v-model:checked="newCollection.privacy_enabled">启用隐私模式（默认模糊）</n-checkbox>
        </div>
        <div class="form-actions">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :disabled="!canCreateCollection" @click="create">创建</n-button>
        </div>
      </n-form>
    </n-modal>

    <n-modal
      v-model:show="showEdit"
      title="编辑集合"
      preset="card"
      :style="{ width: 'min(600px, 92vw)' }"
    >
      <n-form label-placement="top" :show-feedback="false">
        <n-form-item label="集合名称">
          <n-input v-model:value="editForm.name" placeholder="用于前台展示" />
        </n-form-item>
        <n-form-item label="图片来源目录">
          <div class="path-block">
            <div class="path-list">
              <div v-for="path in editForm.paths" :key="path" class="path-row">
                <span class="path-pill">{{ path }}</span>
                <n-button size="tiny" quaternary type="error" @click="removePath(path, 'edit')">移除</n-button>
              </div>
              <div v-if="!editForm.paths.length" class="path-empty">未添加目录</div>
            </div>
            <n-button size="small" quaternary @click="openPicker('edit')">+ 添加目录</n-button>
          </div>
        </n-form-item>
        <n-form-item label="封面路径（可选）">
          <n-input v-model:value="editForm.cover_path" placeholder="留空自动选择封面" />
        </n-form-item>
        <n-form-item label="新密码（可选）">
          <n-input v-model:value="editForm.password" type="password" placeholder="不修改请留空" />
        </n-form-item>
        <n-form-item label="确认新密码">
          <n-input v-model:value="editForm.confirmPassword" type="password" placeholder="再次输入" />
        </n-form-item>
        <div v-if="editPasswordMismatch" class="form-error">两次输入的密码不一致</div>
        <div class="check-list">
          <n-checkbox v-model:checked="editForm.clearPassword">清空访问密码</n-checkbox>
          <n-checkbox v-model:checked="editForm.aggregate_subdirs">包含子目录（递归扫描）</n-checkbox>
          <n-checkbox v-model:checked="editForm.clearCover">清空固定封面</n-checkbox>
          <n-checkbox v-model:checked="editForm.privacy_enabled">启用隐私模式（默认模糊）</n-checkbox>
        </div>
        <div class="form-actions">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" :disabled="!canSaveCollection" @click="save">保存</n-button>
        </div>
      </n-form>
    </n-modal>

    <n-modal
      v-model:show="pickerVisible"
      title="选择目录"
      preset="card"
      :style="{ width: 'min(680px, 94vw)' }"
    >
      <div class="picker-body">
        <div class="picker-bar">
          <n-input
            ref="manualPathInputRef"
            v-model:value="manualPath"
            placeholder="手动输入路径后点添加"
            size="small"
            clearable
            @keydown.enter="addManualPath"
          />
          <n-button size="small" @click="addManualPath">添加</n-button>
        </div>
        <div class="picker-nav">
          <span class="picker-current">{{ pickerPath || '根目录' }}</span>
          <n-button size="tiny" quaternary @click="goUp" :disabled="pickerLoading">上一级</n-button>
          <n-button size="tiny" type="primary" @click="addCurrent" :disabled="!pickerPath">添加当前目录</n-button>
        </div>
        <div class="picker-search">
          <n-input v-model:value="pickerSearch" placeholder="搜索目录" size="small" clearable />
        </div>
        <div class="picker-list">
          <div
            v-for="folder in filteredPickerFolders"
            :key="folder.path"
            class="picker-item"
            @click="enterFolder(folder.path)"
          >
            <div class="picker-name">
              <span class="picker-title">{{ folder.name }}</span>
              <span class="picker-sub">{{ folder.path }}</span>
            </div>
            <n-button size="tiny" quaternary type="primary" @click.stop="addSelected(folder.path)">选择</n-button>
          </div>
          <div v-if="!filteredPickerFolders.length && !pickerLoading" class="picker-empty">没有匹配的目录</div>
        </div>
        <div v-if="pickerLoading" class="picker-loading">加载中...</div>
        <div v-if="pickerError" class="error">{{ pickerError }}</div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import {
  NButton, NInput, NModal, NForm, NFormItem, NPopconfirm, NCheckbox, useNotification
} from 'naive-ui'
import {
  getCollectionsAdmin, createCollection, updateCollection, deleteCollection,
  getFsRoots, listFs, collectionCoverUrl,
  type CollectionAdmin, type FolderItem
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
const manualPathInputRef = ref<{ focus: () => void } | null>(null)

const newCollection = ref({
  name: '', paths: [] as string[], password: '',
  confirmPassword: '', cover_path: '', aggregate_subdirs: false, privacy_enabled: false
})

const editing = ref<CollectionAdmin | null>(null)
const editForm = ref({
  name: '', paths: [] as string[], password: '',
  confirmPassword: '', clearPassword: false, cover_path: '',
  clearCover: false, aggregate_subdirs: false, privacy_enabled: false
})

const filteredPickerFolders = computed(() => {
  const kw = pickerSearch.value.trim().toLowerCase()
  if (!kw) return pickerFolders.value
  return pickerFolders.value.filter(f => f.name.toLowerCase().includes(kw) || f.path.toLowerCase().includes(kw))
})

onMounted(() => load())

function normalizePath(p: string) { return p.replace(/\\/g, '/').trim() }

function getPaths() {
  return pickerTarget.value === 'create' ? newCollection.value.paths : editForm.value.paths
}
function setPaths(paths: string[]) {
  if (pickerTarget.value === 'create') newCollection.value.paths = paths
  else editForm.value.paths = paths
}

function appendPath(path: string) {
  const n = normalizePath(path)
  if (!n) return
  const existing = getPaths()
  if (!existing.includes(n)) setPaths([...existing, n])
}

function removePath(path: string, target: 'create' | 'edit') {
  if (target === 'create') newCollection.value.paths = newCollection.value.paths.filter(p => p !== path)
  else editForm.value.paths = editForm.value.paths.filter(p => p !== path)
}

async function openPicker(target: 'create' | 'edit') {
  pickerTarget.value = target
  pickerSearch.value = ''
  manualPath.value = ''
  pickerVisible.value = true
  await nextTick()
  manualPathInputRef.value?.focus?.()
  await loadRoots()
}

async function loadRoots() {
  pickerLoading.value = true; pickerError.value = ''
  try {
    const roots = await getFsRoots()
    pickerFolders.value = roots.map(r => ({ name: r.name, path: r.path }))
    pickerPath.value = ''; pickerParent.value = ''
  } catch (err: any) {
    pickerError.value = err?.message || '加载失败'
  } finally { pickerLoading.value = false }
}

async function enterFolder(path: string) {
  pickerLoading.value = true; pickerError.value = ''
  try {
    const data = await listFs(path)
    pickerPath.value = data.path; pickerParent.value = data.parent
    pickerFolders.value = data.folders
  } catch (err: any) {
    pickerError.value = err?.message || '加载失败'
  } finally { pickerLoading.value = false }
}

async function goUp() {
  if (!pickerParent.value) { await loadRoots(); return }
  await enterFolder(pickerParent.value)
}

function addCurrent() { if (pickerPath.value) appendPath(pickerPath.value) }
function addSelected(path: string) { appendPath(path) }
function addManualPath() { if (manualPath.value.trim()) { appendPath(manualPath.value); manualPath.value = '' } }

async function load() {
  error.value = ''
  try { collections.value = await getCollectionsAdmin() }
  catch (err: any) { error.value = err?.message || '加载失败' }
}

function openCreate() {
  newCollection.value = { name: '', paths: [], password: '', confirmPassword: '', cover_path: '', aggregate_subdirs: false, privacy_enabled: false }
  showCreate.value = true
}

const createPasswordMismatch = computed(() => {
  const has = Boolean(newCollection.value.password) || Boolean(newCollection.value.confirmPassword)
  return has && newCollection.value.password !== newCollection.value.confirmPassword
})
const canCreateCollection = computed(() => newCollection.value.name.trim() && newCollection.value.paths.length && !createPasswordMismatch.value)

async function create() {
  if (createPasswordMismatch.value) return notification.error({ title: '创建失败', content: '密码不一致' })
  try {
    await createCollection({
      name: newCollection.value.name, paths: newCollection.value.paths,
      password: newCollection.value.password || undefined, cover_path: newCollection.value.cover_path || undefined,
      aggregate_subdirs: newCollection.value.aggregate_subdirs, privacy_enabled: newCollection.value.privacy_enabled
    })
    showCreate.value = false
    notification.success({ title: '已创建', content: newCollection.value.name })
    await load()
  } catch (err: any) { notification.error({ title: '创建失败', content: err?.message || '未知错误' }) }
}

function openEdit(item: CollectionAdmin) {
  editing.value = item
  editForm.value = {
    name: item.name, paths: [...item.paths], password: '', confirmPassword: '',
    clearPassword: false, cover_path: item.cover_path || '', clearCover: false,
    aggregate_subdirs: item.aggregate_subdirs, privacy_enabled: item.privacy_enabled
  }
  showEdit.value = true
}

const editPasswordMismatch = computed(() => {
  const has = Boolean(editForm.value.password) || Boolean(editForm.value.confirmPassword)
  return has && editForm.value.password !== editForm.value.confirmPassword
})
const canSaveCollection = computed(() => editing.value && editForm.value.name.trim() && editForm.value.paths.length && !editPasswordMismatch.value)

async function save() {
  if (!editing.value) return
  if (editPasswordMismatch.value) return notification.error({ title: '更新失败', content: '密码不一致' })
  try {
    await updateCollection(editing.value.id, {
      name: editForm.value.name, paths: editForm.value.paths,
      password: editForm.value.password || undefined, clear_password: editForm.value.clearPassword,
      cover_path: editForm.value.cover_path || undefined, clear_cover: editForm.value.clearCover,
      aggregate_subdirs: editForm.value.aggregate_subdirs, privacy_enabled: editForm.value.privacy_enabled
    })
    showEdit.value = false
    notification.success({ title: '已更新', content: editForm.value.name })
    await load()
  } catch (err: any) { notification.error({ title: '更新失败', content: err?.message || '未知错误' }) }
}

async function remove(id: number) {
  try {
    await deleteCollection(id)
    notification.success({ title: '已删除' })
    await load()
  } catch (err: any) { notification.error({ title: '删除失败', content: err?.message || '未知错误' }) }
}

function onCoverError(event: Event) {
  (event.target as HTMLImageElement)?.classList.add('hidden')
}
</script>

<style scoped>
.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}

.collection-card {
  display: grid;
  grid-template-rows: auto 1fr auto;
  border: 1px solid var(--stroke);
  border-radius: 12px;
  background: var(--panel);
  box-shadow: var(--shadow-tiny);
  overflow: hidden;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.collection-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
}

.cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--placeholder-surface);
  position: relative;
}

.cover img {
  width: 100%; height: 100%; object-fit: cover; display: block;
}

.cover img.hidden { display: none; }

.cover-fallback {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--muted); font-size: 12px; font-weight: 700;
  letter-spacing: 0.06em; text-transform: uppercase;
}
.cover img:not(.hidden) ~ .cover-fallback { opacity: 0; }

.card-body {
  padding: 12px;
  display: grid; gap: 4px;
}

.title {
  font-weight: 700; font-size: 15px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.subtitle {
  font-size: 12px; color: var(--muted);
}

.card-actions {
  display: flex; justify-content: flex-end; gap: 6px;
  padding: 8px 12px 12px;
  border-top: 1px solid rgba(26, 26, 26, 0.05);
}

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 48px 24px; text-align: center;
}

.empty-state-icon { color: rgba(102, 100, 96, 0.25); }

.empty-state-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 16px; font-weight: 700;
}

.empty-state-desc { font-size: 13px; color: var(--muted); }

.path-block { display: grid; gap: 8px; }

.path-list {
  border: 1px solid var(--stroke); border-radius: 8px;
  padding: 4px; display: grid; gap: 2px;
  max-height: 160px; overflow-y: auto;
}

.path-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 8px; padding: 4px 8px; border-radius: 6px;
}

.path-row:hover { background: rgba(26, 26, 26, 0.03); }

.path-pill {
  font-size: 12px; font-family: 'Space Grotesk', Arial, sans-serif;
  color: var(--ink); word-break: break-all;
}

.path-empty {
  padding: 12px; text-align: center; font-size: 12px; color: var(--muted);
}

.check-list {
  display: grid; gap: 8px; padding: 4px 0;
}

.form-error { font-size: 12px; color: #b00020; margin-top: -8px; }

.form-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  padding-top: 8px; border-top: 1px solid var(--stroke);
}

.picker-body { display: grid; gap: 10px; }

.picker-bar {
  display: flex; gap: 8px; align-items: center;
}

.picker-nav {
  display: flex; align-items: center; gap: 8px;
}

.picker-current {
  flex: 1; min-width: 0;
  font-size: 12px; color: var(--muted);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.picker-list {
  border: 1px solid var(--stroke); border-radius: 8px;
  max-height: 280px; overflow-y: auto;
}

.picker-item {
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px; padding: 8px 10px; cursor: pointer;
  border-bottom: 1px solid rgba(26, 26, 26, 0.04);
}

.picker-item:last-child { border-bottom: none; }

.picker-item:hover { background: rgba(26, 26, 26, 0.03); }

.picker-name { display: grid; gap: 2px; min-width: 0; }

.picker-title { font-weight: 600; font-size: 13px; }

.picker-sub {
  font-size: 11px; color: var(--muted);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.picker-empty, .picker-loading {
  padding: 24px; text-align: center; font-size: 12px; color: var(--muted);
}

@media (max-width: 960px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }

  .picker-bar { flex-direction: column; }
}
</style>
