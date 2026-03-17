import { onBeforeUnmount, onMounted, ref, unref, watch, type Ref } from 'vue'

type StorageKeySource = string | Ref<string>
type PrivacySyncDetail = {
  storageKey: string
}
const PRIVACY_SYNC_EVENT = 'image-views:privacy-reveal-sync'

function readStoredMap(storageKey: string) {
  if (typeof window === 'undefined' || !storageKey) {
    return {} as Record<string, true>
  }
  try {
    const raw = window.sessionStorage.getItem(storageKey)
    if (!raw) return {}
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return {}
    return parsed.reduce<Record<string, true>>((acc, item) => {
      if (typeof item === 'string' && item) {
        acc[item] = true
      }
      return acc
    }, {})
  } catch {
    return {}
  }
}

function writeStoredMap(storageKey: string, map: Record<string, true>) {
  if (typeof window === 'undefined' || !storageKey) {
    return
  }
  const keys = Object.keys(map)
  if (!keys.length) {
    window.sessionStorage.removeItem(storageKey)
    return
  }
  window.sessionStorage.setItem(storageKey, JSON.stringify(keys))
}

export function usePrivacyReveal(storageKeySource: StorageKeySource) {
  const revealedMap = ref<Record<string, true>>({})

  function syncFromStorage() {
    revealedMap.value = readStoredMap(unref(storageKeySource))
  }

  function persist(next: Record<string, true>) {
    const storageKey = unref(storageKeySource)
    revealedMap.value = next
    writeStoredMap(storageKey, next)
    if (typeof window !== 'undefined' && storageKey) {
      window.dispatchEvent(
        new CustomEvent<PrivacySyncDetail>(PRIVACY_SYNC_EVENT, {
          detail: { storageKey }
        })
      )
    }
  }

  function syncFromSyncEvent(event: Event) {
    const detail = (event as CustomEvent<PrivacySyncDetail>).detail
    const currentKey = unref(storageKeySource)
    if (!currentKey) {
      return
    }
    if (detail?.storageKey !== currentKey) {
      return
    }
    syncFromStorage()
  }

  function isRevealed(key: string) {
    return Boolean(revealedMap.value[key])
  }

  function reveal(key: string) {
    if (!key || isRevealed(key)) {
      return false
    }
    const next = {
      ...revealedMap.value,
      [key]: true
    }
    persist(next)
    return true
  }

  function revealMany(keys: string[]) {
    const uniqueKeys = Array.from(new Set(keys.filter(Boolean)))
    if (!uniqueKeys.length) {
      return false
    }
    let changed = false
    const next = { ...revealedMap.value }
    for (const key of uniqueKeys) {
      if (!next[key]) {
        next[key] = true
        changed = true
      }
    }
    if (!changed) {
      return false
    }
    persist(next)
    return true
  }

  function hide(key: string) {
    if (!key || !isRevealed(key)) {
      return false
    }
    const next = { ...revealedMap.value }
    delete next[key]
    persist(next)
    return true
  }

  function hideMany(keys: string[]) {
    const uniqueKeys = Array.from(new Set(keys.filter(Boolean)))
    if (!uniqueKeys.length) {
      return false
    }
    let changed = false
    const next = { ...revealedMap.value }
    for (const key of uniqueKeys) {
      if (next[key]) {
        delete next[key]
        changed = true
      }
    }
    if (!changed) {
      return false
    }
    persist(next)
    return true
  }

  function reset() {
    const storageKey = unref(storageKeySource)
    if (!storageKey && !Object.keys(revealedMap.value).length) {
      return false
    }
    persist({})
    return true
  }

  watch(() => unref(storageKeySource), syncFromStorage, { immediate: true })
  onMounted(() => {
    if (typeof window === 'undefined') {
      return
    }
    window.addEventListener(PRIVACY_SYNC_EVENT, syncFromSyncEvent)
  })
  onBeforeUnmount(() => {
    if (typeof window === 'undefined') {
      return
    }
    window.removeEventListener(PRIVACY_SYNC_EVENT, syncFromSyncEvent)
  })

  return {
    isRevealed,
    reveal,
    revealMany,
    hide,
    hideMany,
    reset
  }
}
