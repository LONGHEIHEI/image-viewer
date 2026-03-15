<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">集合管理</div>
      <div class="page-actions">
        <n-button @click="load">刷新</n-button>
        <n-button type="primary" @click="openCreate">新增集合</n-button>
      </div>
    </div>

    <n-card class="panel" :bordered="false">
      <n-list bordered>
        <n-list-item v-for="item in collections" :key="item.id">
          <div class="row">
            <div>
              <div class="name">{{ item.name }}</div>
              <div class="meta">编号：{{ item.id }}</div>
              <div class="meta">路径：{{ item.paths.join(', ') }}</div>
              <div class="meta">密码：{{ item.requires_password ? '已设置' : '无' }}</div>
            </div>
            <n-space size="small">
              <n-button size="small" @click="openEdit(item)">编辑</n-button>
              <n-popconfirm @positive-click="remove(item.id)" positive-text="删除" negative-text="取消">
                <template #trigger>
                  <n-button size="small" type="error">删除</n-button>
                </template>
                确认删除该集合？
              </n-popconfirm>
            </n-space>
          </div>
        </n-list-item>
      </n-list>

      <div v-if="error" class="error">{{ error }}</div>
    </n-card>

    <n-modal v-model:show="showCreate" preset="card" title="新增集合" class="modal">
      <n-form>
        <n-form-item label="集合名称">
          <n-input v-model:value="newCollection.name" placeholder="请输入集合名称" />
        </n-form-item>
        <n-form-item label="集合路径">
          <n-input
            v-model:value="newCollection.paths"
            type="textarea"
            placeholder="用逗号分隔，例如：set1, set2/sub"
          />
        </n-form-item>
        <n-form-item label="访问密码">
          <n-input v-model:value="newCollection.password" type="password" placeholder="可留空" />
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" @click="create">创建</n-button>
        </n-space>
      </n-form>
    </n-modal>

    <n-modal v-model:show="showEdit" preset="card" title="编辑集合" class="modal">
      <n-form>
        <n-form-item label="集合名称">
          <n-input v-model:value="editForm.name" placeholder="请输入集合名称" />
        </n-form-item>
        <n-form-item label="集合路径">
          <n-input v-model:value="editForm.paths" type="textarea" placeholder="用逗号分隔" />
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="editForm.password" type="password" placeholder="不修改请留空" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.clearPassword">清空密码</n-checkbox>
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" @click="save">保存</n-button>
        </n-space>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  NCard,
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
  type CollectionAdmin
} from '../api/client'

const collections = ref<CollectionAdmin[]>([])
const error = ref('')
const notification = useNotification()

const showCreate = ref(false)
const showEdit = ref(false)

const newCollection = ref({
  name: '',
  paths: '',
  password: ''
})

const editing = ref<CollectionAdmin | null>(null)
const editForm = ref({
  name: '',
  paths: '',
  password: '',
  clearPassword: false
})

onMounted(() => {
  load()
})

function parsePaths(input: string) {
  return input
    .split(',')
    .map((p) => p.trim())
    .filter(Boolean)
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
  newCollection.value = { name: '', paths: '', password: '' }
  showCreate.value = true
}

async function create() {
  error.value = ''
  try {
    await createCollection({
      name: newCollection.value.name,
      paths: parsePaths(newCollection.value.paths),
      password: newCollection.value.password || undefined
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
    paths: item.paths.join(', '),
    password: '',
    clearPassword: false
  }
  showEdit.value = true
}

async function save() {
  if (!editing.value) return
  error.value = ''
  try {
    await updateCollection(editing.value.id, {
      name: editForm.value.name,
      paths: parsePaths(editForm.value.paths),
      password: editForm.value.password || undefined,
      clear_password: editForm.value.clearPassword
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
</script>

<style scoped>
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.name {
  font-weight: 700;
}

.modal {
  width: min(560px, 92vw);
}
</style>
