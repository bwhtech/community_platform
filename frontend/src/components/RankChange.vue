<template>
  <span v-if="previousRank === null" class="text-xs text-ink-blue-6">New</span>
  <span v-else-if="delta > 0" class="inline-flex items-center text-xs tabular-nums text-ink-green-6">
    <span class="lucide-arrow-up size-3" aria-hidden="true" />{{ delta }}
    <span class="sr-only">places up</span>
  </span>
  <span v-else-if="delta < 0" class="inline-flex items-center text-xs tabular-nums text-ink-red-6">
    <span class="lucide-arrow-down size-3" aria-hidden="true" />{{ -delta }}
    <span class="sr-only">places down</span>
  </span>
  <span v-else class="text-xs text-ink-gray-4" aria-label="No change">–</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rank: { type: Number, required: true },
  previousRank: { type: Number, default: null },
})

const delta = computed(() => props.previousRank - props.rank)
</script>
