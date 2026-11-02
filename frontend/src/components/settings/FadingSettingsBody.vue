<template>
  <SettingsBody ref="body" class="scroll-fade" :class="{ 'fade-top': fadeTop, 'fade-bottom': fadeBottom }">
    <slot />
  </SettingsBody>
</template>

<script setup>
import { computed, ref, useTemplateRef } from 'vue'
import { useEventListener, useResizeObserver } from '@vueuse/core'
import { SettingsBody } from 'frappe-ui'

// SettingsBody scrolls with a hard edge under the pinned header, so rows look
// cut off mid-scroll. Fade each edge that still has content past it.
const body = useTemplateRef('body')
const viewport = computed(() => body.value?.viewportElement ?? null)
// The viewport keeps its size; the content inside it grows as data loads.
const content = computed(() => viewport.value?.firstElementChild ?? null)

const fadeTop = ref(false)
const fadeBottom = ref(false)

function update() {
  const el = viewport.value
  if (!el) return
  fadeTop.value = el.scrollTop > 0
  fadeBottom.value = Math.ceil(el.scrollTop + el.clientHeight) < el.scrollHeight
}

useEventListener(viewport, 'scroll', update, { passive: true })
useResizeObserver(viewport, update)
useResizeObserver(content, update)
</script>
