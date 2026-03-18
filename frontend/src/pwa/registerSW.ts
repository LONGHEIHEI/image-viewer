import { registerSW as register } from 'virtual:pwa-register'
import {
  markPwaNeedRefresh,
  markPwaOfflineReady,
  setPwaUpdateServiceWorker
} from './updateState'

export function registerSW() {
  const updateSW = register({
    immediate: true,
    onNeedRefresh() {
      markPwaNeedRefresh(true)
    },
    onOfflineReady() {
      markPwaOfflineReady(true)
    }
  })
  setPwaUpdateServiceWorker(updateSW)
}
