type CacheEntry<T> = {
  value: T
  expiresAt: number
  updatedAt: number
}

type CacheReadResult<T> = {
  value: T
  isExpired: boolean
}

const CACHE_PREFIX = 'image-views:local-cache:v1:'
const CACHE_INDEX_KEY = `${CACHE_PREFIX}index`
const MAX_CACHE_ENTRIES = 80

function getStorage() {
  if (typeof window === 'undefined') return null
  try {
    return window.localStorage
  } catch {
    return null
  }
}

function getCacheKey(key: string) {
  return `${CACHE_PREFIX}${key}`
}

function readIndex(storage: Storage) {
  const raw = storage.getItem(CACHE_INDEX_KEY)
  if (!raw) return [] as string[]
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === 'string') : []
  } catch {
    storage.removeItem(CACHE_INDEX_KEY)
    return []
  }
}

function writeIndex(storage: Storage, keys: string[]) {
  storage.setItem(CACHE_INDEX_KEY, JSON.stringify(keys))
}

function removeIndexedKey(storage: Storage, key: string) {
  writeIndex(
    storage,
    readIndex(storage).filter((item) => item !== key)
  )
}

function touchIndexedKey(storage: Storage, key: string) {
  const keys = readIndex(storage).filter((item) => item !== key)
  keys.push(key)
  while (keys.length > MAX_CACHE_ENTRIES) {
    const staleKey = keys.shift()
    if (staleKey) {
      storage.removeItem(getCacheKey(staleKey))
    }
  }
  writeIndex(storage, keys)
}

function removeCacheKey(storage: Storage, key: string) {
  storage.removeItem(getCacheKey(key))
  removeIndexedKey(storage, key)
}

export function readLocalCache<T>(key: string, allowExpired = false): CacheReadResult<T> | null {
  const storage = getStorage()
  if (!storage) return null
  const raw = storage.getItem(getCacheKey(key))
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw) as CacheEntry<T>
    const isExpired = parsed.expiresAt <= Date.now()
    if (isExpired && !allowExpired) {
      removeCacheKey(storage, key)
      return null
    }
    touchIndexedKey(storage, key)
    return {
      value: parsed.value,
      isExpired
    }
  } catch {
    removeCacheKey(storage, key)
    return null
  }
}

export function writeLocalCache<T>(key: string, value: T, ttlMs: number) {
  const storage = getStorage()
  if (!storage) return
  const payload: CacheEntry<T> = {
    value,
    expiresAt: Date.now() + ttlMs,
    updatedAt: Date.now()
  }
  const serialized = JSON.stringify(payload)

  try {
    storage.setItem(getCacheKey(key), serialized)
    touchIndexedKey(storage, key)
    return
  } catch {
    const keys = readIndex(storage)
    while (keys.length > 0) {
      const staleKey = keys.shift()
      if (staleKey) {
        storage.removeItem(getCacheKey(staleKey))
      }
      try {
        storage.setItem(getCacheKey(key), serialized)
        keys.push(key)
        writeIndex(storage, keys)
        return
      } catch {
        // Keep evicting older entries until there is enough room.
      }
    }
  }
}

export function clearLocalCache() {
  const storage = getStorage()
  if (!storage) return
  for (const key of readIndex(storage)) {
    storage.removeItem(getCacheKey(key))
  }
  storage.removeItem(CACHE_INDEX_KEY)
}
