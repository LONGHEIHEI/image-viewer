import { ref, unref, watch, type Ref } from 'vue'

type StorageKeySource = string | Ref<string>

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
    revealedMap.value = next
    writeStoredMap(unref(storageKeySource), next)
    return true
  }

  watch(() => unref(storageKeySource), syncFromStorage, { immediate: true })

  return {
    isRevealed,
    reveal
  }
}
