<template>
  <div v-if="rows.length" class="divide-y divide-outline-gray-1">
    <div v-for="row in rows" :key="row.id" class="flex items-start gap-3 py-3">
      <span class="mt-0.5 grid size-7 shrink-0 place-content-center rounded-full bg-surface-gray-2 text-ink-gray-6">
        <span :class="actionMeta(row.action).icon" class="size-3.5" aria-hidden="true" />
      </span>
      <div class="min-w-0 flex-1">
        <RouterLink
          v-if="row.url?.startsWith('/')"
          :to="row.url"
          class="block truncate text-base text-ink-gray-8 hover:underline"
        >
          {{ row.title }}
        </RouterLink>
        <a
          v-else-if="row.url"
          :href="row.url"
          target="_blank"
          rel="noopener"
          class="block truncate text-base text-ink-gray-8 hover:underline"
        >
          {{ row.title }}
        </a>
        <p v-else class="truncate text-base text-ink-gray-8">{{ row.title }}</p>
        <div class="mt-1.5 flex flex-wrap items-center gap-x-1.5 text-sm text-ink-gray-5">
          <span>{{ actionMeta(row.action).label }}</span>
          <template v-if="repoOf(row.externalId)">
            <span aria-hidden="true">·</span>
            <span>{{ repoOf(row.externalId) }}</span>
          </template>
          <template v-if="row.productInfo">
            <span aria-hidden="true">·</span>
            <span class="inline-flex items-center gap-1">
              <ProductLogo :product="row.productInfo" size="xs" />{{ row.productInfo.name }}
            </span>
          </template>
          <span aria-hidden="true">·</span>
          <span>{{ formatDate(row.date) }}</span>
        </div>
      </div>
      <div class="shrink-0 text-right">
        <span class="text-sm-semibold tabular-nums" :class="row.revoked ? 'text-ink-gray-4 line-through' : 'text-ink-gray-7'">
          +{{ row.points }}
        </span>
        <p v-if="row.revoked" class="mt-1 text-xs text-ink-gray-5">Revoked</p>
      </div>
    </div>
  </div>
  <div v-else class="py-10 text-center text-sm text-ink-gray-5">{{ emptyText }}</div>
</template>

<script setup>
import ProductLogo from '@/components/ProductLogo.vue'
import { actionMeta, repoOf } from '@/utils/actions'
import { formatDate } from '@/utils/dates'

defineProps({
  rows: { type: Array, required: true },
  emptyText: { type: String, default: 'No activity yet' },
})
</script>
