<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">集合设置</div>
      <div class="page-actions">
        <n-button type="primary" @click="openCreate">新增集合</n-button>
      </div>
    </div>

    <section class="admin-section">
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
            <div class="subtitle">已配置 {{ item.paths.length }} 个目录</div>
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
    </section>

    <n-modal
      v-model:show="showCreate"
      title="新增集合"
      :trap-focus="!pickerVisible"
      :style="{ width: 'min(600px, 92vw)' }"
      :transition-name="null"
      :mask-transition-name="null"
    >
      <n-form class="flat-form modal-surface" label-placement="top" :show-feedback="false">
        <n-form-item label="集合名称">
          <n-input v-model:value="newCollection.name" placeholder="用于前台展示，例如：家庭相册" />
        </n-form-item>
        <n-form-item label="图片来源目录">
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
            <n-button size="small" @click="openPicker('create')">添加目录</n-button>
          </div>
        </n-form-item>
        <n-form-item label="固定封面路径">
          <n-input
            v-model:value="newCollection.cover_path"
            placeholder="可选；留空时系统会自动选择封面"
          />
        </n-form-item>
        <n-form-item label="访问密码（可选）">
          <n-input v-model:value="newCollection.password" type="password" placeholder="留空表示公开访问" />
        </n-form-item>
        <n-form-item label="确认访问密码">
          <n-input v-model:value="newCollection.confirmPassword" type="password" placeholder="请再次输入访问密码" />
        </n-form-item>
        <div v-if="createPasswordMismatch" class="form-tip form-tip--error">两次输入的访问密码不一致</div>
        <div class="check-list">
          <div class="option-item">
            <n-checkbox v-model:checked="newCollection.aggregate_subdirs">包含子目录（递归）</n-checkbox>
            <div class="option-tip">开启后会自动扫描并展示所选目录下的全部子目录内容。</div>
          </div>
          <div class="option-item">
            <n-checkbox v-model:checked="newCollection.privacy_enabled">启用隐私模式（默认模糊）</n-checkbox>
            <div class="option-tip">列表缩略图默认模糊，点击后才会显示清晰图片。</div>
          </div>
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
      :trap-focus="!pickerVisible"
      :style="{ width: 'min(600px, 92vw)' }"
      :transition-name="null"
      :mask-transition-name="null"
    >
      <n-form class="flat-form modal-surface" label-placement="top" :show-feedback="false">
        <n-form-item label="集合名称">
          <n-input v-model:value="editForm.name" placeholder="用于前台展示，例如：家庭相册" />
        </n-form-item>
        <n-form-item label="图片来源目录">
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
            <n-button size="small" @click="openPicker('edit')">添加目录</n-button>
          </div>
        </n-form-item>
        <n-form-item label="固定封面路径">
          <n-input
            v-model:value="editForm.cover_path"
            placeholder="可选；留空时系统会自动选择封面"
          />
        </n-form-item>
        <n-form-item label="新访问密码">
          <n-input v-model:value="editForm.password" type="password" placeholder="不修改请留空" />
        </n-form-item>
        <n-form-item label="确认新访问密码">
          <n-input v-model:value="editForm.confirmPassword" type="password" placeholder="请再次输入新访问密码" />
        </n-form-item>
        <div v-if="editPasswordMismatch" class="form-tip form-tip--error">两次输入的新访问密码不一致</div>
        <div class="check-list">
          <div class="option-item">
            <n-checkbox v-model:checked="editForm.clearPassword">清空访问密码</n-checkbox>
            <div class="option-tip">保存后该集合将不再需要密码即可访问。</div>
          </div>
          <div class="option-item">
            <n-checkbox v-model:checked="editForm.aggregate_subdirs">包含子目录（递归）</n-checkbox>
            <div class="option-tip">开启后会自动扫描并展示所选目录下的全部子目录内容。</div>
          </div>
          <div class="option-item">
            <n-checkbox v-model:checked="editForm.clearCover">清空固定封面</n-checkbox>
            <div class="option-tip">保存后将取消手动封面并恢复自动选择。</div>
          </div>
          <div class="option-item">
            <n-checkbox v-model:checked="editForm.privacy_enabled">启用隐私模式（默认模糊）</n-checkbox>
            <div class="option-tip">列表缩略图默认模糊，点击后才会显示清晰图片。</div>
          </div>
        </div>
        <div class="form-actions">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" :disabled="!canSaveCollection" @click="save">保存</n-button>
        </div>
      </n-form>
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
          <n-input
            ref="manualPathInputRef"
            v-model:value="manualPath"
            placeholder="手动输入路径"
            clearable
          />
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
import { computed, nextTick, onMounted, ref } from 'vue'
import {
  NButton,
  NList,
  NListItem,
  NInput,
  NModal,
  NForm,
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
const manualPathInputRef = ref<{ focus: () => void } | null>(null)

const newCollection = ref({
  name: '',
  paths: [] as string[],
  password: '',
  confirmPassword: '',
  cover_path: '',
  aggregate_subdirs: false,
  privacy_enabled: false
})

const editing = ref<CollectionAdmin | null>(null)
const editForm = ref({
  name: '',
  paths: [] as string[],
  password: '',
  confirmPassword: '',
  clearPassword: false,
  cover_path: '',
  clearCover: false,
  aggregate_subdirs: false,
  privacy_enabled: false
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
  await nextTick()
  manualPathInputRef.value?.focus?.()
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
    confirmPassword: '',
    cover_path: '',
    aggregate_subdirs: false,
    privacy_enabled: false
  }
  showCreate.value = true
}

const createPasswordMismatch = computed(() => {
  const hasInput = Boolean(newCollection.value.password) || Boolean(newCollection.value.confirmPassword)
  if (!hasInput) return false
  return newCollection.value.password !== newCollection.value.confirmPassword
})

const canCreateCollection = computed(() => {
  if (!newCollection.value.name.trim()) return false
  if (!newCollection.value.paths.length) return false
  return !createPasswordMismatch.value
})

async function create() {
  if (createPasswordMismatch.value) {
    notification.error({ title: '创建失败', content: '两次输入的访问密码不一致' })
    return
  }
  error.value = ''
  try {
    await createCollection({
      name: newCollection.value.name,
      paths: newCollection.value.paths,
      password: newCollection.value.password || undefined,
      cover_path: newCollection.value.cover_path || undefined,
      aggregate_subdirs: newCollection.value.aggregate_subdirs,
      privacy_enabled: newCollection.value.privacy_enabled
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
    confirmPassword: '',
    clearPassword: false,
    cover_path: item.cover_path || '',
    clearCover: false,
    aggregate_subdirs: item.aggregate_subdirs,
    privacy_enabled: item.privacy_enabled
  }
  showEdit.value = true
}

const editPasswordMismatch = computed(() => {
  const hasInput = Boolean(editForm.value.password) || Boolean(editForm.value.confirmPassword)
  if (!hasInput) return false
  return editForm.value.password !== editForm.value.confirmPassword
})

const canSaveCollection = computed(() => {
  if (!editing.value) return false
  if (!editForm.value.name.trim()) return false
  if (!editForm.value.paths.length) return false
  return !editPasswordMismatch.value
})

async function save() {
  if (!editing.value) return
  if (editPasswordMismatch.value) {
    notification.error({ title: '更新失败', content: '两次输入的新访问密码不一致' })
    return
  }
  error.value = ''
  try {
    await updateCollection(editing.value.id, {
      name: editForm.value.name,
      paths: editForm.value.paths,
      password: editForm.value.password || undefined,
      clear_password: editForm.value.clearPassword,
      cover_path: editForm.value.cover_path || undefined,
      clear_cover: editForm.value.clearCover,
      aggregate_subdirs: editForm.value.aggregate_subdirs,
      privacy_enabled: editForm.value.privacy_enabled
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

.admin-section {
  display: grid;
  gap: 8px;
}

.cover {
  width: 124px;
  height: 74px;
  border: 1px solid var(--stroke);
  border-radius: 10px;
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
  grid-template-columns: 1fr;
  gap: 10px;
}

.collection-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border: 1px solid rgba(27, 30, 39, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 4px 12px rgba(20, 25, 35, 0.04);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.collection-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(20, 25, 35, 0.08);
}

.card-body {
  display: grid;
  gap: 2px;
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
  line-height: 1.35;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-actions {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  align-items: flex-end;
}

.name {
  font-weight: 700;
}

.folder-block {
  display: grid;
  gap: 4px;
  width: 100%;
}

.path-list :deep(.n-list) {
  border: 1px solid var(--stroke);
  border-radius: 8px;
  background: transparent;
}

.path-list :deep(.n-list-item) {
  padding: 4px 6px;
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
  gap: 6px;
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
  gap: 4px;
  grid-template-columns: 1fr auto;
  align-items: center;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
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
  gap: 6px;
  flex-wrap: wrap;
}

.picker-list {
  height: 280px;
  max-height: 280px;
  min-height: 240px;
  overflow-y: scroll;
  overflow-x: hidden;
  scrollbar-gutter: stable;
}

.picker-list :deep(.n-list-item) {
  padding: 6px 8px;
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
  gap: 8px;
  padding: 4px 0 0;
}

.form-tip {
  font-size: 12px;
  margin-top: -6px;
}

.form-tip--error {
  color: #b00020;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
  padding-top: 0;
}

.check-list {
  display: grid;
  gap: 6px;
  padding-top: 1px;
}

.option-item {
  display: grid;
  gap: 2px;
  padding: 6px 8px;
  border: 1px solid var(--stroke);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.55);
}

.option-tip {
  font-size: 11px;
  line-height: 1.4;
  color: var(--muted);
  padding-left: 24px;
}

.check-list :deep(.n-checkbox) {
  min-height: 24px;
}

.check-list :deep(.n-checkbox__label) {
  line-height: 1.2;
}

.flat-form :deep(.n-form-item) {
  margin: 0;
}

.flat-form :deep(.n-form-item-label) {
  font-size: 12px;
  font-weight: 600;
  padding-bottom: 1px;
}

.flat-form :deep(.n-form-item-blank) {
  margin-top: 0;
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
  padding: 4px 6px;
  border-radius: 0;
  border: none;
  background: transparent;
}

.modal-surface {
  background: #fff;
  border: 1px solid var(--stroke);
  border-radius: 10px;
  padding: 8px 10px;
  box-shadow: none;
}

@media (max-width: 960px) {
  .row {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .card-actions {
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    flex-wrap: wrap;
  }

  .card-actions > * {
    flex: 0 0 auto;
  }

  .collection-card {
    grid-template-columns: 1fr;
    align-items: stretch;
    gap: 8px;
  }

  .cover {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 9;
  }

  .picker-input {
    grid-template-columns: 1fr;
  }

  .picker-list {
    height: min(300px, 46vh);
    max-height: min(300px, 46vh);
    min-height: 220px;
  }

  .picker-search {
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .collection-card {
    padding: 8px;
  }

  .picker-header {
    align-items: flex-start;
  }

  .picker-header :deep(.n-space) {
    width: 100%;
  }
}
/* Desktop-first card layout for collection settings */
.collections-grid {
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.collection-card {
  grid-template-columns: 1fr;
  grid-template-rows: auto 1fr auto;
  align-items: stretch;
  gap: 0;
  padding: 0;
  border: 1px solid var(--stroke);
  border-radius: 14px;
  background: var(--panel);
  box-shadow: var(--shadow-tiny);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

.collection-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-soft);
}

.cover {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  border: none;
  border-radius: 0;
}

.card-body {
  padding: 10px 12px 8px;
  gap: 4px;
}

.card-actions {
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 12px 12px;
  border-top: 1px solid rgba(27, 30, 39, 0.06);
}

@media (max-width: 960px) {
  .collections-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
  }

  .card-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }
}

/* Unified spacing rhythm for settings pages: 12 / 8 / 6 */
.admin-section {
  gap: 12px;
}

.collections-grid {
  gap: 12px;
}

.collection-card {
  border-radius: 12px;
}

.card-body {
  padding: 12px;
  gap: 6px;
}

.card-actions {
  gap: 6px;
  padding: 8px 12px 12px;
}

.flat-form {
  gap: 8px;
}

.check-list {
  gap: 6px;
}

.option-item {
  gap: 2px;
  padding: 8px;
}

.form-actions {
  gap: 8px;
}

.picker {
  gap: 8px;
}
</style>
