<template>
  <div class="divide-y divide-outline-gray-1">
    <RequestRow v-for="request in requests" :key="request.id" :request="request" :show-trend="showTrend" />
  </div>
</template>

<script setup>
import RequestRow from '@/components/requests/RequestRow.vue'

defineProps({
  requests: { type: Array, required: true },
  showTrend: { type: Boolean, default: false },
})
</script>
