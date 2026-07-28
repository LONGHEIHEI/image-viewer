<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">用户管理</div>
      <div class="page-actions">
        <n-input
          v-model:value="keyword"
          placeholder="搜索用户名或路径"
          size="small"
          clearable
          class="user-search"
        />
        <n-select
          v-model:value="roleFilter"
          :options="roleOptions"
          size="small"
          class="role-filter"
        />
        <n-button type="primary" size="small" @click="openCreate">新增用户</n-button>
      </div>
    </div>

    <div class="user-list" v-if="filteredUsers.length">
      <div v-for="user in filteredUsers" :key="user.id" class="user-card">
        <div class="user-main">
          <div class="user-name">
            {{ user.username }}
            <span v-if="currentUserId === user.id" class="self-tag">当前账号</span>
            <span class="role-tag" :class="user.is_admin ? 'role-tag--admin' : 'role-tag--user'">
              {{ user.is_admin ? '管理员' : '普通用户' }}
            </span>
          </div>
          <div class="user-meta" v-if="user.created_at">创建于 {{ formatTime(user.created_at) }}</div>
          <div class="user-paths" v-if="(user.allowed_paths || []).length">
            <span class="user-paths-label">允许路径</span>
            <span class="user-path" v-for="p in (user.allowed_paths || [])" :key="p">{{ p }}</span>
          </div>
          <div class="user-meta user-meta--all" v-else>允许访问所有路径</div>
        </div>
        <div class="user-actions">
          <n-button size="small" quaternary @click="openEdit(user)">编辑</n-button>
          <n-popconfirm
            v-if="currentUserId !== user.id"
            @positive-click="remove(user.id)"
            positive-text="删除"
            negative-text="取消"
          >
            <template #trigger>
              <n-button size="small" quaternary type="error">删除</n-button>
            </template>
            确认删除该用户？
          </n-popconfirm>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
      <div class="empty-state-title">暂无匹配用户</div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <n-modal v-model:show="showCreate" title="新增用户" preset="card" :style="{ width: 'min(480px, 92vw)' }">
      <n-form label-placement="top" :show-feedback="false">
        <n-form-item label="用户名">
          <n-input v-model:value="newUser.username" placeholder="请输入用户名" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="newUser.password" type="password" show-password-on="click" placeholder="至少 6 位" />
        </n-form-item>
        <n-form-item label="确认密码">
          <n-input v-model:value="newUser.confirmPassword" type="password" show-password-on="click" placeholder="再次输入" />
        </n-form-item>
        <div v-if="createPasswordMismatch" class="form-error">两次输入的密码不一致</div>
        <n-form-item>
          <n-checkbox v-model:checked="newUser.is_admin">管理员权限</n-checkbox>
        </n-form-item>
        <n-form-item label="允许访问路径（可选）">
          <n-input
            v-model:value="newUser.allowedPaths"
            type="textarea"
            placeholder="逗号分隔，留空允许全部"
            :autosize="{ minRows: 2, maxRows: 4 }"
          />
        </n-form-item>
        <div class="form-actions">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :disabled="!canCreate" @click="create">创建</n-button>
        </div>
      </n-form>
    </n-modal>

    <n-modal v-model:show="showEdit" title="编辑用户" preset="card" :style="{ width: 'min(480px, 92vw)' }">
      <n-form label-placement="top" :show-feedback="false">
        <n-form-item label="用户名">
          <n-input :value="editing?.username" disabled />
        </n-form-item>
        <n-form-item>
          <n-checkbox v-model:checked="editForm.is_admin">管理员权限</n-checkbox>
        </n-form-item>
        <n-form-item label="新密码（可选）">
          <n-input v-model:value="editForm.password" type="password" show-password-on="click" placeholder="不修改请留空" />
        </n-form-item>
        <n-form-item label="确认新密码">
          <n-input v-model:value="editForm.confirmPassword" type="password" show-password-on="click" placeholder="再次输入" />
        </n-form-item>
        <div v-if="editPasswordMismatch" class="form-error">两次输入的密码不一致</div>
        <n-form-item label="允许访问路径">
          <n-input
            v-model:value="editForm.allowedPaths"
            type="textarea"
            placeholder="逗号分隔，留空允许全部"
            :autosize="{ minRows: 2, maxRows: 4 }"
          />
        </n-form-item>
        <div class="form-actions">
          <n-button @click="showEdit = false">取消</n-button>
          <n-button type="primary" :disabled="!canSave" @click="save">保存</n-button>
        </div>
      </n-form>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  NButton, NInput, NCheckbox, NModal, NForm, NFormItem, NPopconfirm, NSelect, useNotification
} from 'naive-ui'
import { listUsers, createUser, updateUser, deleteUser, type UserInfo } from '../api/client'
import { useAuthStore } from '../store/auth'

const users = ref<UserInfo[]>([])
const error = ref('')
const loading = ref(false)
const notification = useNotification()
const auth = useAuthStore()
const currentUserId = computed(() => auth.user?.id ?? null)

const keyword = ref('')
const roleFilter = ref<'all' | 'admin' | 'user'>('all')
const roleOptions = [
  { label: '全部角色', value: 'all' },
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' }
]

const filteredUsers = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return users.value.filter(u => {
    if (roleFilter.value === 'admin' && !u.is_admin) return false
    if (roleFilter.value === 'user' && u.is_admin) return false
    if (!kw) return true
    if (u.username.toLowerCase().includes(kw)) return true
    return (u.allowed_paths || []).some(p => p.toLowerCase().includes(kw))
  })
})

const showCreate = ref(false)
const showEdit = ref(false)

const newUser = ref({
  username: '', password: '', confirmPassword: '',
  is_admin: false, allowedPaths: ''
})

const editing = ref<UserInfo | null>(null)
const editForm = ref({
  is_admin: false, password: '', confirmPassword: '', allowedPaths: ''
})

onMounted(() => load())

function formatTime(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function parsePaths(input: string) { return input.split(',').map(p => p.trim()).filter(Boolean) }

async function load() {
  error.value = ''
  try { loading.value = true; users.value = await listUsers() }
  catch (err: any) { error.value = err?.message || '加载失败' }
  finally { loading.value = false }
}

function openCreate() {
  newUser.value = { username: '', password: '', confirmPassword: '', is_admin: false, allowedPaths: '' }
  showCreate.value = true
}

const createPasswordMismatch = computed(() => {
  const has = Boolean(newUser.value.password) || Boolean(newUser.value.confirmPassword)
  return has && newUser.value.password !== newUser.value.confirmPassword
})

const canCreate = computed(() => newUser.value.username.trim() && newUser.value.password.length >= 6 && !createPasswordMismatch.value)

async function create() {
  if (createPasswordMismatch.value) return notification.error({ title: '创建失败', content: '密码不一致' })
  try {
    await createUser({
      username: newUser.value.username, password: newUser.value.password,
      is_admin: newUser.value.is_admin, allowed_paths: parsePaths(newUser.value.allowedPaths)
    })
    showCreate.value = false
    notification.success({ title: '已创建', content: newUser.value.username })
    newUser.value = { username: '', password: '', confirmPassword: '', is_admin: false, allowedPaths: '' }
    await load()
  } catch (err: any) { notification.error({ title: '创建失败', content: err?.message || '未知错误' }) }
}

function openEdit(user: UserInfo) {
  editing.value = user
  editForm.value = {
    is_admin: user.is_admin, password: '', confirmPassword: '',
    allowedPaths: (user.allowed_paths || []).join(', ')
  }
  showEdit.value = true
}

const editPasswordMismatch = computed(() => {
  const has = Boolean(editForm.value.password) || Boolean(editForm.value.confirmPassword)
  return has && editForm.value.password !== editForm.value.confirmPassword
})

const canSave = computed(() => {
  if (!editing.value) return false
  if (editForm.value.password && editForm.value.password.length < 6) return false
  if (editPasswordMismatch.value) return false
  if (currentUserId.value === editing.value.id && editing.value.is_admin && !editForm.value.is_admin) return false
  return true
})

async function save() {
  if (!editing.value) return
  if (editPasswordMismatch.value) return notification.error({ title: '更新失败', content: '密码不一致' })
  try {
    await updateUser(editing.value.id, {
      is_admin: editForm.value.is_admin,
      password: editForm.value.password || undefined,
      allowed_paths: parsePaths(editForm.value.allowedPaths)
    })
    showEdit.value = false
    notification.success({ title: '已更新', content: editing.value.username })
    editing.value = null
    await load()
  } catch (err: any) { notification.error({ title: '更新失败', content: err?.message || '未知错误' }) }
}

async function remove(userId: number) {
  try {
    await deleteUser(userId)
    notification.success({ title: '已删除' })
    await load()
  } catch (err: any) { notification.error({ title: '删除失败', content: err?.message || '未知错误' }) }
}
</script>

<style scoped>
.user-list {
  display: grid; gap: 8px;
}

.user-card {
  display: flex; justify-content: space-between; align-items: flex-start;
  gap: 12px; padding: 14px 16px;
  border: 1px solid var(--stroke); border-radius: 12px;
  background: var(--panel); box-shadow: var(--shadow-tiny);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.user-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-soft);
}

.user-main {
  display: grid; gap: 6px; min-width: 0;
}

.user-name {
  font-weight: 700; font-size: 15px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}

.self-tag {
  font-size: 10px; padding: 2px 7px; border-radius: 999px;
  border: 1px solid var(--stroke); color: var(--muted);
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
}

.role-tag {
  font-size: 10px; padding: 2px 7px; border-radius: 999px;
  font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;
}

.role-tag--admin {
  background: rgba(194, 101, 75, 0.1); color: #c2654b;
  border: 1px solid rgba(194, 101, 75, 0.2);
}

.role-tag--user {
  background: rgba(102, 100, 96, 0.06); color: var(--muted);
  border: 1px solid var(--stroke);
}

.user-meta {
  font-size: 12px; color: var(--muted);
}

.user-meta--all { font-style: italic; }

.user-paths {
  display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}

.user-paths-label {
  font-size: 11px; color: var(--muted); font-weight: 600;
}

.user-path {
  font-size: 11px; padding: 2px 7px; border-radius: 5px;
  background: rgba(102, 100, 96, 0.06); color: var(--ink);
  font-family: 'Space Grotesk', Arial, sans-serif; word-break: break-all;
}

.user-actions {
  display: flex; gap: 4px; flex-shrink: 0;
}

.user-search { width: 200px; }
.role-filter { width: 110px; }

.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 48px 24px; text-align: center;
}

.empty-state-icon { color: rgba(102, 100, 96, 0.25); }

.empty-state-title {
  font-family: 'Space Grotesk', Arial, sans-serif;
  font-size: 16px; font-weight: 700;
}

.form-error { font-size: 12px; color: #b00020; margin-top: -8px; }

.form-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  padding-top: 8px; border-top: 1px solid var(--stroke);
}

@media (max-width: 960px) {
  .user-card { flex-direction: column; }
  .user-actions { width: 100%; justify-content: flex-end; }
  .user-search { width: 100%; }
  .role-filter { width: 100%; }
}
</style>
