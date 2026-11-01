<template>
  <img
    v-if="product"
    :src="product.logo"
    :alt="decorative ? '' : product.name"
    class="shrink-0 rounded-1 object-contain"
    :class="sizeClass"
  />
  <span v-else class="lucide-globe shrink-0 text-ink-gray-5" :class="sizeClass" aria-hidden="true" />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  product: { type: Object, default: null },
  size: { type: String, default: 'sm' },
  decorative: { type: Boolean, default: true },
})

const sizeClass = computed(() => ({ xs: 'size-3.5', sm: 'size-4', md: 'size-5', lg: 'size-8' })[props.size])
</script>
