import type { RouteLocationNormalizedLoaded, Router } from 'vue-router'
import {
  archiveThumbUrl,
  collectionArchiveThumbUrl,
  collectionThumbUrl,
  thumbUrl,
  type FavoriteItem,
  type FavoritePayload
} from '../api/client'

function basename(value: string) {
  const parts = value.split(/[\\/]+/).filter(Boolean)
  return parts[parts.length - 1] || value
}

function getStoredCollectionToken(collectionId: number | null) {
  if (collectionId === null) return ''
  return localStorage.getItem(`collection_token_${collectionId}`) || ''
}

export function buildFavoriteKey(
  favorite: Pick<FavoritePayload, 'source_kind' | 'collection_id' | 'container_path' | 'item_path'>
) {
  return [
    favorite.source_kind,
    String(favorite.collection_id || 0),
    favorite.container_path || '',
    favorite.item_path
  ].join('::')
}

export function favoriteToPayload(item: FavoriteItem): FavoritePayload {
  return {
    source_kind: item.source_kind,
    collection_id: item.collection_id ?? null,
    container_path: item.container_path,
    item_path: item.item_path,
    folder_path: item.folder_path,
    view_mode: item.view_mode,
    item_name: item.item_name
  }
}

export function favoriteSourceLabel(item: { source_kind: string }) {
  switch (item.source_kind) {
    case 'archive_image':
      return '压缩包图片'
    case 'collection_image':
      return '图集图片'
    case 'collection_archive_image':
      return '图集压缩包图片'
    default:
      return '普通图片'
  }
}

export function favoriteDisplayPath(item: Pick<FavoriteItem, 'source_kind' | 'container_path' | 'item_path'>) {
  if (item.source_kind === 'archive_image' || item.source_kind === 'collection_archive_image') {
    return `${item.container_path} :: ${item.item_path}`
  }
  return item.item_path
}

export function favoriteThumbUrl(item: FavoriteItem) {
  switch (item.source_kind) {
    case 'archive_image':
      return archiveThumbUrl(item.container_path, item.item_path)
    case 'collection_image':
      return collectionThumbUrl(item.collection_id as number, item.item_path)
    case 'collection_archive_image':
      return collectionArchiveThumbUrl(item.collection_id as number, item.container_path, item.item_path)
    default:
      return thumbUrl(item.item_path)
  }
}

export function openFavorite(router: Router, item: FavoriteItem) {
  if (item.source_kind === 'archive_image' || item.source_kind === 'collection_archive_image') {
    const query: Record<string, string> = {
      archive: item.container_path,
      file: item.item_path
    }
    if (item.folder_path) {
      query.folder = item.folder_path
    }
    if (item.collection_id) {
      query.collection = String(item.collection_id)
      query.view = item.view_mode || 'folder'
    }
    router.push({ path: '/image', query })
    return
  }

  const query: Record<string, string> = {
    path: item.item_path
  }
  if (item.folder_path) {
    query.folder = item.folder_path
  }
  if (item.collection_id) {
    query.collection = String(item.collection_id)
    query.view = item.view_mode || 'folder'
  }
  router.push({ path: '/image', query })
}

export function favoritePayloadFromRoute(
  route: RouteLocationNormalizedLoaded,
  itemName = ''
): FavoritePayload | null {
  const rawCollectionId = route.query.collection
  const collectionId =
    rawCollectionId === undefined || rawCollectionId === null || rawCollectionId === ''
      ? null
      : Number(rawCollectionId)
  const resolvedCollectionId = Number.isFinite(collectionId) ? collectionId : null
  const archive = String(route.query.archive || '')
  const file = String(route.query.file || '')
  const path = String(route.query.path || '')
  const folderPath = String(route.query.folder || '')
  const viewMode = route.query.view === 'flat' ? 'flat' : 'folder'

  if (archive && file) {
    return {
      source_kind: resolvedCollectionId ? 'collection_archive_image' : 'archive_image',
      collection_id: resolvedCollectionId,
      container_path: archive,
      item_path: file,
      folder_path: folderPath,
      view_mode: viewMode,
      item_name: itemName || basename(file),
      collection_token: getStoredCollectionToken(resolvedCollectionId)
    }
  }

  if (!path) return null

  return {
    source_kind: resolvedCollectionId ? 'collection_image' : 'image',
    collection_id: resolvedCollectionId,
    item_path: path,
    folder_path: folderPath,
    view_mode: viewMode,
    item_name: itemName || basename(path),
    collection_token: getStoredCollectionToken(resolvedCollectionId)
  }
}
