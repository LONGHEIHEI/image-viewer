import { ref } from 'vue'

type UpdateServiceWorker = ((reloadPage?: boolean) => Promise<void>) | undefined

const needRefresh = ref(false)
const offlineReady = ref(false)
const updateServiceWorker = ref<UpdateServiceWorker>()

export function usePwaUpdateState() {
  async function applyUpdate() {
    if (!updateServiceWorker.value) return
    await updateServiceWorker.value(true)
    needRefresh.value = false
  }

  function dismissRefreshPrompt() {
    needRefresh.value = false
  }

  function dismissOfflineReady() {
    offlineReady.value = false
  }

  return {
    needRefresh,
    offlineReady,
    applyUpdate,
    dismissRefreshPrompt,
    dismissOfflineReady
  }
}

export function setPwaUpdateServiceWorker(fn: UpdateServiceWorker) {
  updateServiceWorker.value = fn
}

export function markPwaNeedRefresh(value: boolean) {
  needRefresh.value = value
}

export function markPwaOfflineReady(value: boolean) {
  offlineReady.value = value
}
