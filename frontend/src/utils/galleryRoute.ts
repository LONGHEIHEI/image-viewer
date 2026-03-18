import type { LocationQueryValue } from 'vue-router'

export type GalleryViewMode = 'folder' | 'flat'

type ImageRouteQueryOptions = {
  index: number
  path?: string
  archive?: string
  file?: string
  folder?: string
  collectionId?: number | null
  view?: GalleryViewMode
  privacyEnabled?: boolean
}

function firstQueryValue(value: unknown): LocationQueryValue | undefined {
  if (Array.isArray(value)) {
    return value[0]
  }
  return typeof value === 'string' ? value : undefined
}

export function readQueryString(value: unknown): string {
  return firstQueryValue(value) || ''
}

export function parseCollectionId(value: unknown): number | null {
  const raw = readQueryString(value)
  if (!raw) return null
  const parsed = Number(raw)
  return Number.isFinite(parsed) ? parsed : null
}

export function parseGalleryView(value: unknown): GalleryViewMode {
  return readQueryString(value) === 'flat' ? 'flat' : 'folder'
}

export function getParentFolderFromPath(path: string): string {
  return path.split('/').slice(0, -1).join('/')
}

export function getPathBasename(path: string): string {
  const parts = path.split(/[\\/]+/).filter(Boolean)
  return parts[parts.length - 1] || path
}

// Keep image-view query assembly in one place so folder/archive/collection
// navigation keeps the same contract when we add new route flags later.
export function buildImageRouteQuery(options: ImageRouteQueryOptions): Record<string, string> {
  const query: Record<string, string> = {
    index: String(options.index)
  }

  if (options.privacyEnabled) {
    query.privacy = '1'
  }

  if (options.archive) {
    query.archive = options.archive
    query.file = options.file || ''
    if (options.folder) {
      query.folder = options.folder
    }
  } else if (options.path) {
    query.path = options.path
    if (options.folder) {
      query.folder = options.folder
    }
  }

  if (options.collectionId !== null && options.collectionId !== undefined) {
    query.collection = String(options.collectionId)
    query.view = options.view === 'flat' ? 'flat' : 'folder'
  }

  return query
}
