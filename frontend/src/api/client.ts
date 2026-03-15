export type FolderItem = {
  name: string
  path: string
}

export type FolderListing = {
  folder: string
  folders: FolderItem[]
  images: FolderItem[]
  archives: FolderItem[]
  page: number
  page_size: number
  total_images: number
  has_more: boolean
}

export type ArchiveListing = {
  archive: string
  files: FolderItem[]
  page: number
  page_size: number
  total_files: number
  has_more: boolean
}

export type TreeNode = {
  name: string
  path: string
  type: 'folder' | 'archive'
  children?: TreeNode[]
}

export type UserInfo = {
  id: number
  username: string
  is_admin: boolean
  allowed_paths: string[]
}

const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('token') || ''
}

function tokenQuery() {
  const token = getToken()
  return token ? `&token=${encodeURIComponent(token)}` : ''
}

async function requestJson(url: string, options: RequestInit = {}) {
  const token = getToken()
  const headers = new Headers(options.headers || {})
  headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || '请求失败')
  }
  return res.json()
}

export async function login(username: string, password: string) {
  return requestJson(`${API_BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ username, password })
  })
}

export async function getMe(): Promise<UserInfo> {
  return requestJson(`${API_BASE}/auth/me`)
}

export async function getTree(root = '', depth = 2): Promise<TreeNode> {
  const url = `${API_BASE}/tree?root=${encodeURIComponent(root)}&depth=${depth}`
  return requestJson(url)
}

export async function getFolder(path = '', page = 1, pageSize = 60): Promise<FolderListing> {
  const url = `${API_BASE}/folder?path=${encodeURIComponent(path)}&page=${page}&page_size=${pageSize}`
  return requestJson(url)
}

export async function getArchive(path: string, page = 1, pageSize = 80): Promise<ArchiveListing> {
  const url = `${API_BASE}/archive?path=${encodeURIComponent(path)}&page=${page}&page_size=${pageSize}`
  return requestJson(url)
}

export async function listUsers(): Promise<UserInfo[]> {
  return requestJson(`${API_BASE}/users`)
}

export async function createUser(payload: {
  username: string
  password: string
  is_admin: boolean
  allowed_paths: string[]
}) {
  return requestJson(`${API_BASE}/users`, {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export async function updateUser(userId: number, payload: {
  password?: string
  is_admin?: boolean
  allowed_paths?: string[]
}) {
  return requestJson(`${API_BASE}/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  })
}

export async function deleteUser(userId: number) {
  return requestJson(`${API_BASE}/users/${userId}`, {
    method: 'DELETE'
  })
}

export function imageUrl(path: string): string {
  return `${API_BASE}/image?path=${encodeURIComponent(path)}${tokenQuery()}`
}

export function archiveImageUrl(archive: string, file: string): string {
  return `${API_BASE}/archive/image?path=${encodeURIComponent(archive)}&file=${encodeURIComponent(file)}${tokenQuery()}`
}

export function thumbUrl(path: string): string {
  return `${API_BASE}/thumb?path=${encodeURIComponent(path)}${tokenQuery()}`
}

export function archiveThumbUrl(archive: string, file: string): string {
  return `${API_BASE}/archive/thumb?path=${encodeURIComponent(archive)}&file=${encodeURIComponent(file)}${tokenQuery()}`
}
