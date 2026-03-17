<template>
  <button
    type="button"
    :class="['privacy-eye-button', { 'privacy-eye-button--active': active }]"
    :title="title"
    :aria-label="title"
    :aria-pressed="active ? 'true' : 'false'"
    @click="$emit('click')"
  >
    <svg class="privacy-eye-svg" viewBox="0 0 24 24" aria-hidden="true">
      <path class="privacy-eye-outline" d="M2 12c1.9-3.5 5.4-5.8 10-5.8s8.1 2.3 10 5.8c-1.9 3.5-5.4 5.8-10 5.8S3.9 15.5 2 12Z" />
      <circle class="privacy-eye-pupil" cx="12" cy="12" r="2.7" />
      <path class="privacy-eye-slash" d="M4.5 19.5L19.5 4.5" />
    </svg>
  </button>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  active?: boolean
}>()

defineEmits<{
  (event: 'click'): void
}>()
</script>

<style scoped>
.privacy-eye-button {
  --eye-color: rgba(47, 143, 124, 0.96);
  appearance: none;
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid rgba(27, 30, 39, 0.12);
  background: rgba(255, 255, 255, 0.9);
  color: var(--eye-color);
  box-shadow: 0 8px 18px rgba(20, 25, 35, 0.12);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease,
    background 0.16s ease,
    border-color 0.16s ease,
    color 0.16s ease;
}

.privacy-eye-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 11px 22px rgba(20, 25, 35, 0.16);
}

.privacy-eye-button:active {
  transform: translateY(0) scale(0.98);
}

.privacy-eye-button--active {
  --eye-color: rgba(255, 106, 61, 0.94);
  border-color: rgba(255, 106, 61, 0.34);
  background: rgba(255, 248, 244, 0.94);
  box-shadow: 0 10px 20px rgba(255, 106, 61, 0.18);
}

.privacy-eye-button:focus-visible {
  outline: 2px solid rgba(47, 143, 124, 0.28);
  outline-offset: 2px;
}

.privacy-eye-svg {
  width: 20px;
  height: 20px;
  overflow: visible;
}

.privacy-eye-outline {
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.privacy-eye-slash {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  transform-origin: 50% 50%;
  transform: scale(0.7);
  opacity: 0;
  transition: transform 0.16s ease, opacity 0.16s ease;
}

.privacy-eye-pupil {
  fill: currentColor;
  transform-origin: 50% 50%;
  transition: transform 0.16s ease, opacity 0.16s ease;
}

.privacy-eye-button--active .privacy-eye-pupil {
  opacity: 0.22;
  transform: scale(0.72);
}

.privacy-eye-button--active .privacy-eye-slash {
  opacity: 1;
  transform: scale(1);
}

@media (prefers-reduced-motion: reduce) {
  .privacy-eye-button,
  .privacy-eye-slash,
  .privacy-eye-pupil {
    transition: none;
  }
}
</style>
