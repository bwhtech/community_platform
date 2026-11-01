<template>
  <Tooltip :text="summary">
    <div class="flex h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-2">
      <span
        v-for="part in parts"
        :key="part.value"
        :class="part.color"
        :style="{ width: `${part.share}%` }"
      />
    </div>
  </Tooltip>
</template>

<script setup>
import { computed } from 'vue'
import { Tooltip } from 'frappe-ui'
import { SOURCES } from '@/utils/sources'

const props = defineProps({ bySource: { type: Object, required: true } })

const parts = computed(() => {
  const total = Object.values(props.bySource).reduce((sum, p) => sum + Math.max(p, 0), 0)
  return SOURCES.filter((s) => props.bySource[s.value] > 0).map((s) => ({
    ...s,
    points: props.bySource[s.value],
    share: (props.bySource[s.value] / total) * 100,
  }))
})

const summary = computed(() => parts.value.map((p) => `${p.label} ${p.points}`).join(' · '))
</script>
