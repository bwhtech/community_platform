<template>
  <div class="relative -mx-3 flex items-start gap-4 rounded-4 px-3 py-4 hover:bg-surface-gray-1">
    <RouterLink :to="`/requests/${request.id}`" class="absolute inset-0 rounded-4" :aria-label="request.title" />
    <UpvoteButton :request="request" />
    <div class="min-w-0 flex-1">
      <p class="text-base-semibold text-ink-gray-8">
        {{ request.title }}
        <Badge v-if="request.hidden" class="ml-1" theme="red" label="Hidden" size="sm" />
      </p>
      <p class="mt-1.5 line-clamp-2 text-p-sm text-ink-gray-6">{{ request.description }}</p>
      <div class="mt-2 flex flex-wrap items-center gap-x-1.5 gap-y-1 text-sm text-ink-gray-5">
        <span class="inline-flex items-center gap-1">
          <ProductLogo :product="request.productInfo" size="xs" />{{ request.productInfo?.name }}
        </span>
        <span aria-hidden="true">·</span>
        <span>{{ request.author.fullName }}</span>
        <span aria-hidden="true">·</span>
        <span>{{ timeAgo(request.createdAt) }}</span>
        <template v-if="showTrend && request.recentUpvotes">
          <span aria-hidden="true">·</span>
          <span class="text-ink-gray-7">+{{ request.recentUpvotes }} this week</span>
        </template>
      </div>
    </div>
    <div class="hidden shrink-0 sm:block">
      <ReactionBar :request="request" readonly />
    </div>
  </div>
</template>

<script setup>
import { Badge } from 'frappe-ui'
import ProductLogo from '@/components/ProductLogo.vue'
import ReactionBar from '@/components/ReactionBar.vue'
import UpvoteButton from '@/components/UpvoteButton.vue'
import { timeAgo } from '@/utils/dates'

defineProps({
  request: { type: Object, required: true },
  showTrend: { type: Boolean, default: false },
})
</script>
