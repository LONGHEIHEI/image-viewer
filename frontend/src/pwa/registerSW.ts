import { registerSW as register } from 'virtual:pwa-register'

export function registerSW() {
  register({
    immediate: true
  })
}
