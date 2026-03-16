<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">用户</div>
      <div class="page-actions">
        <n-button type="primary" @click="openCreate">新增用户</n-button>
      </div>
    </div>

    <section class="admin-section">
      <n-list :bordered="false" class="user-list">
        <n-list-item v-for="user in users" :key="user.id">
          <div class="row">
            <div>
              <div class="name">{{ user.username }}</div>
              <div class="meta">编号：{{ user.id }}</div>
              <div class="meta">权限：{{ user.is_admin ? '管理员' : '普通用户' }}</div>
              <div class="meta">允许路径：{{ (user.allowed_paths || []).join(', ') || '全部' }}</div>
            </div>
            <n-space size="small">
              <n-button size="small" @click="openEdit(user)">编辑</n-button>
              <n-popconfirm @positive-click="remove(user.id)" positive-text="删除" negative-text="取消">
                <template #trigger>
                  <n-button size="small" type="error">删除</n-button>
                </template>
                确认删除该用户？
              </n-popconfirm>
            </n-space>
          </div>
        </n-list-item>
      </n-list>

      <div v-if="error" class="error">{{ error }}</div>
    </section>

    <n-modal v-model:show="showCreate" preset="card" title="新增用户" class="modal">
      <n-form>
        <n-form-item label="用户名">
          <n-input v-model:value="newUser.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="newUser.password" type="password" placeholder="请输入密码" />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="newUser.is_admin">管理员</n-checkbox>
        </n-form-item>
        <n-form-item label="允许访问路径">
          <n-input
            v-model:value="newUser.allowedPaths"
            type="textarea"
            placeholder="用逗号分隔，例如：set1, set2/sub"
          />
        </n-form-item>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" @click="create">创建</n-button>
        </n-space>
      </n-form>
    </n-modal>

    <n-modal v-model:show="showEdit" preset="card" title="编辑用户" class="modal">
      <n-form>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.is_admin">管理员</n-checkbox>
        </n-form-item>
        <n-form-item label="新密码">
          <n-input v-model:value="editForm.password" type="password" placeholder="不修改请留空" />
        </n-form-item>
        <n-form-item label="允许访问路径">
          <n-input v-model:value="editForm.allowedPaths" type="textarea" placeholder="用逗号分隔" />
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
  NButton,
  NList,
  NListItem,
  NInput,
  NCheckbox,
  NModal,
  NForm,
  NFormItem,
  NSpace,
  NPopconfirm,
  useNotification
} from 'naive-ui'
import { listUsers, createUser, updateUser, deleteUser, type UserInfo } from '../api/client'

const users = ref<UserInfo[]>([])
const error = ref('')
const notification = useNotification()

const showCreate = ref(false)
const showEdit = ref(false)

const newUser = ref({
  username: '',
  password: '',
  is_admin: false,
  allowedPaths: ''
})

const editing = ref<UserInfo | null>(null)
const editForm = ref({
  is_admin: false,
  password: '',
  allowedPaths: ''
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
    users.value = await listUsers()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载失败'
    notification.error({ title: '加载失败', content: error.value })
  }
}

function openCreate() {
  newUser.value = { username: '', password: '', is_admin: false, allowedPaths: '' }
  showCreate.value = true
}

async function create() {
  error.value = ''
  try {
    await createUser({
      username: newUser.value.username,
      password: newUser.value.password,
      is_admin: newUser.value.is_admin,
      allowed_paths: parsePaths(newUser.value.allowedPaths)
    })
    showCreate.value = false
    notification.success({ title: '创建成功', content: `用户 ${newUser.value.username} 已创建` })
    newUser.value = { username: '', password: '', is_admin: false, allowedPaths: '' }
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建失败'
    notification.error({ title: '创建失败', content: error.value })
  }
}

function openEdit(user: UserInfo) {
  editing.value = user
  editForm.value = {
    is_admin: user.is_admin,
    password: '',
    allowedPaths: (user.allowed_paths || []).join(', ')
  }
  showEdit.value = true
}

async function save() {
  if (!editing.value) return
  error.value = ''
  try {
    await updateUser(editing.value.id, {
      is_admin: editForm.value.is_admin,
      password: editForm.value.password || undefined,
      allowed_paths: parsePaths(editForm.value.allowedPaths)
    })
    showEdit.value = false
    notification.success({ title: '更新成功', content: `已更新用户 ${editing.value.username}` })
    editing.value = null
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '更新失败'
    notification.error({ title: '更新失败', content: error.value })
  }
}

async function remove(userId: number) {
  error.value = ''
  try {
    await deleteUser(userId)
    notification.success({ title: '删除成功', content: '用户已删除' })
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

.admin-section {
  display: grid;
  gap: 12px;
}

.user-list {
  border-top: 1px solid rgba(27, 30, 39, 0.08);
}

.user-list :deep(.n-list-item) {
  padding: 14px 0;
  border-bottom: 1px solid rgba(27, 30, 39, 0.08);
}

.name {
  font-weight: 700;
}

.modal {
  width: min(520px, 92vw);
}

@media (max-width: 960px) {
  .row {
    flex-direction: column;
    align-items: flex-start;
  }

  .row :deep(.n-space) {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
