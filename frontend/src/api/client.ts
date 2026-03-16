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

export type CollectionSummary = {
  id: number
  name: string
  requires_password: boolean
  cover_path?: string | null
  aggregate_subdirs?: boolean
  privacy_enabled?: boolean
}

export type CollectionAdmin = {
  id: number
  name: string
  paths: string[]
  requires_password: boolean
  cover_path?: string | null
  aggregate_subdirs: boolean
  privacy_enabled: boolean
  created_at: string
}

export type FsRoot = {
  name: string
  path: string
}

export type FsList = {
  path: string
  parent: string
  folders: FolderItem[]
}

const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('token') || ''
}

function tokenQuery() {
  const token = getToken()
  return token ? `&token=${encodeURIComponent(token)}` : ''
}

function getCollectionToken(collectionId: number | string) {
  return localStorage.getItem(`collection_token_${collectionId}`) || ''
}

export function setCollectionToken(collectionId: number | string, token: string) {
  if (token) {
    localStorage.setItem(`collection_token_${collectionId}`, token)
  } else {
    localStorage.removeItem(`collection_token_${collectionId}`)
  }
}

function collectionTokenQuery(collectionId: number | string) {
  const token = getCollectionToken(collectionId)
  return token ? `&ct=${encodeURIComponent(token)}` : ''
}

async function requestJson(url: string, options: RequestInit = {}) {
  const token = getToken()
  const headers = new Headers(options.headers || {})
  headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    const text = await res.text()
    try {
      const data = JSON.parse(text)
      if (data && typeof data.detail === 'string') {
        throw new Error(data.detail)
      }
    } catch {
      // ignore parse errors
    }
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

export async function getCollectionsAvailable(): Promise<CollectionSummary[]> {
  return requestJson(`${API_BASE}/collections/available`)
}

export async function getCollectionsAdmin(): Promise<CollectionAdmin[]> {
  return requestJson(`${API_BASE}/collections`)
}

export async function getFsRoots(): Promise<FsRoot[]> {
  const data = await requestJson(`${API_BASE}/fs/roots`)
  return data.roots || []
}

export async function listFs(path: string): Promise<FsList> {
  return requestJson(`${API_BASE}/fs/list?path=${encodeURIComponent(path)}`)
}

export async function getCollectionInfo(collectionId: number): Promise<CollectionSummary> {
  return requestJson(`${API_BASE}/collections/${collectionId}`)
}

export async function createCollection(payload: {
  name: string
  paths: string[]
  password?: string
  cover_path?: string
  aggregate_subdirs?: boolean
  privacy_enabled?: boolean
}) {
  return requestJson(`${API_BASE}/collections`, {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export async function updateCollection(
  collectionId: number,
  payload: {
    name?: string
    paths?: string[]
    password?: string
    clear_password?: boolean
    cover_path?: string
    clear_cover?: boolean
    aggregate_subdirs?: boolean
    privacy_enabled?: boolean
  }
) {
  return requestJson(`${API_BASE}/collections/${collectionId}`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  })
}

export async function deleteCollection(collectionId: number) {
  return requestJson(`${API_BASE}/collections/${collectionId}`, {
    method: 'DELETE'
  })
}

export async function accessCollection(collectionId: number, password?: string) {
  return requestJson(`${API_BASE}/collections/${collectionId}/access`, {
    method: 'POST',
    body: JSON.stringify({ password: password || '' })
  })
}

export async function getCollectionFolder(
  collectionId: number,
  path = '',
  page = 1,
  pageSize = 60,
  view: 'folder' | 'flat' = 'folder'
): Promise<FolderListing> {
  const viewQuery = view === 'flat' ? '&view=flat' : ''
  const url = `${API_BASE}/collections/${collectionId}/folder?path=${encodeURIComponent(path)}&page=${page}&page_size=${pageSize}${viewQuery}${collectionTokenQuery(collectionId)}`
  return requestJson(url)
}

export async function getCollectionArchive(
  collectionId: number,
  path: string,
  page = 1,
  pageSize = 80
): Promise<ArchiveListing> {
  const url = `${API_BASE}/collections/${collectionId}/archive?path=${encodeURIComponent(path)}&page=${page}&page_size=${pageSize}${collectionTokenQuery(collectionId)}`
  return requestJson(url)
}

export async function getCollectionTree(collectionId: number, depth = 2): Promise<TreeNode> {
  const url = `${API_BASE}/collections/${collectionId}/tree?depth=${depth}${collectionTokenQuery(collectionId)}`
  return requestJson(url)
}

export function folderCoverUrl(path: string): string {
  return `${API_BASE}/folder/cover?path=${encodeURIComponent(path)}${tokenQuery()}`
}

export function collectionFolderCoverUrl(collectionId: number, path: string): string {
  return `${API_BASE}/collections/${collectionId}/folder/cover?path=${encodeURIComponent(path)}${collectionTokenQuery(collectionId)}${tokenQuery()}`
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

export function archiveCoverUrl(archive: string): string {
  return `${API_BASE}/archive/cover?path=${encodeURIComponent(archive)}${tokenQuery()}`
}

export function collectionImageUrl(collectionId: number, path: string): string {
  return `${API_BASE}/collections/${collectionId}/image?path=${encodeURIComponent(path)}${collectionTokenQuery(collectionId)}${tokenQuery()}`
}

export function collectionArchiveImageUrl(collectionId: number, archive: string, file: string): string {
  return `${API_BASE}/collections/${collectionId}/archive/image?path=${encodeURIComponent(archive)}&file=${encodeURIComponent(file)}${collectionTokenQuery(collectionId)}${tokenQuery()}`
}

export function collectionThumbUrl(collectionId: number, path: string): string {
  return `${API_BASE}/collections/${collectionId}/thumb?path=${encodeURIComponent(path)}${collectionTokenQuery(collectionId)}${tokenQuery()}`
}

export function collectionArchiveThumbUrl(collectionId: number, archive: string, file: string): string {
  return `${API_BASE}/collections/${collectionId}/archive/thumb?path=${encodeURIComponent(archive)}&file=${encodeURIComponent(file)}${collectionTokenQuery(collectionId)}${tokenQuery()}`
}

export function collectionArchiveCoverUrl(collectionId: number, archive: string): string {
  return `${API_BASE}/collections/${collectionId}/archive/cover?path=${encodeURIComponent(archive)}${collectionTokenQuery(collectionId)}${tokenQuery()}`
}

export function collectionCoverUrl(collectionId: number | string): string {
  const token = getToken()
  if (token) {
    return `${API_BASE}/collections/${collectionId}/cover?token=${encodeURIComponent(token)}`
  }
  return `${API_BASE}/collections/${collectionId}/cover`
}
