<template>
  <ListRow class="h-16" :route="`/u/${row.login}`" :class="{ 'bg-surface-gray-1': isMe }">
    <ListCell class="flex-col !items-start justify-center gap-1">
      <span class="text-base tabular-nums text-ink-gray-7">{{ row.rank }}</span>
      <RankChange :rank="row.rank" :previous-rank="row.previousRank" />
    </ListCell>
    <ListCell class="gap-3">
      <Avatar :label="row.fullName" :image="row.avatar" size="lg" />
      <span class="min-w-0">
        <span class="flex items-center gap-1.5 truncate text-base text-ink-gray-8">
          {{ row.fullName }}
          <Badge v-if="isMe" label="You" size="sm" />
        </span>
        <span class="mt-1.5 block truncate text-sm text-ink-gray-5">
          {{ highlights(row.counts) || `@${row.login}` }}
        </span>
      </span>
    </ListCell>
    <ListCell class="max-md:hidden">
      <SourceBar :by-source="row.bySource" />
    </ListCell>
    <ListCell class="justify-end text-lg-semibold tabular-nums text-ink-gray-9">
      {{ row.points.toLocaleString() }}
    </ListCell>
  </ListRow>
</template>

<script setup>
import { Avatar, Badge } from 'frappe-ui'
import { ListCell, ListRow } from 'frappe-ui/list'
import RankChange from '@/components/RankChange.vue'
import SourceBar from '@/components/SourceBar.vue'
import { highlights } from '@/utils/actions'

defineProps({
  row: { type: Object, required: true },
  isMe: { type: Boolean, default: false },
})
</script>
