<template>
  <span
    class="inline-grid shrink-0 place-content-center rounded-full"
    :class="[sizeClasses.box, COLORS[badge.color] ?? COLORS.gray, { 'opacity-40 grayscale': locked }]"
  >
    <span :class="[badge.icon, sizeClasses.icon]" aria-hidden="true" />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  badge: { type: Object, required: true },
  size: { type: String, default: 'md' },
  locked: { type: Boolean, default: false },
})

const COLORS = {
  green: 'bg-surface-green-2 text-ink-green-6',
  blue: 'bg-surface-blue-2 text-ink-blue-6',
  violet: 'bg-surface-violet-2 text-ink-violet-6',
  amber: 'bg-surface-amber-2 text-ink-amber-6',
  red: 'bg-surface-red-2 text-ink-red-6',
  gray: 'bg-surface-gray-2 text-ink-gray-7',
}

const sizeClasses = computed(
  () =>
    ({
      sm: { box: 'size-7', icon: 'size-3.5' },
      md: { box: 'size-10', icon: 'size-5' },
      lg: { box: 'size-14', icon: 'size-7' },
    })[props.size],
)
</script>
