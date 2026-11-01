<template>
  <AppHeader title="Point ledger" />

  <div class="mx-auto max-w-[1080px] px-3 pb-20 pt-5 sm:px-5">
    <p class="max-w-2xl text-p-base text-ink-gray-6">
      Every point ever awarded. Rows are never edited: a revoke adds a negative row with a reason, so totals and
      past leaderboards stay explainable.
    </p>

    <div class="mt-5 flex flex-wrap items-center gap-2">
      <TabButtons v-model="source" :options="sourceOptions" />
      <div class="w-60">
        <Select v-model="login" :options="contributorOptions" placeholder="All contributors" />
      </div>
      <Button v-if="login" variant="ghost" icon-left="lucide-x" label="Clear" @click="login = null" />
    </div>

    <div class="-mx-3 mt-4 overflow-x-auto">
      <List class="min-w-[42rem] list-row-px-3" :columns="['6.5rem', 'minmax(0,11rem)', 'minmax(0,1fr)', '4rem', '3rem']">
        <ListHeader>
          <ListHeaderCell>Date</ListHeaderCell>
          <ListHeaderCell>Contributor</ListHeaderCell>
          <ListHeaderCell>Activity</ListHeaderCell>
          <ListHeaderCell class="justify-end">Points</ListHeaderCell>
          <ListHeaderCell />
        </ListHeader>
        <ListRows :items="ledger.rows" row-key="id" v-slot="{ item }">
          <ListRow class="py-2.5">
            <ListCell class="text-sm tabular-nums text-ink-gray-5">{{ formatDate(item.date) }}</ListCell>
            <ListCell class="gap-2">
              <Avatar :label="item.person.fullName" :image="item.person.avatar" size="xs" />
              <RouterLink :to="`/u/${item.login}`" class="truncate text-sm text-ink-gray-7 hover:underline">
                {{ item.person.fullName }}
              </RouterLink>
            </ListCell>
            <ListCell>
              <span class="min-w-0">
                <span class="block truncate text-sm text-ink-gray-8">{{ item.title }}</span>
                <span class="mt-1 block truncate text-xs text-ink-gray-5">
                  {{ item.isRevoke ? `Revoked: ${item.reason}` : actionMeta(item.action).label }}
                  <template v-if="item.revoked"> · revoked</template>
                </span>
              </span>
            </ListCell>
            <ListCell
              class="justify-end text-sm-semibold tabular-nums"
              :class="item.points < 0 ? 'text-ink-red-6' : item.revoked ? 'text-ink-gray-4 line-through' : 'text-ink-gray-8'"
            >
              {{ item.points > 0 ? '+' : '' }}{{ item.points }}
            </ListCell>
            <ListCell class="justify-end">
              <Button
                v-if="!item.isRevoke && !item.revoked"
                variant="ghost"
                icon="lucide-undo-2"
                tooltip="Revoke"
                :aria-label="`Revoke ${item.title}`"
                @click="revoke(item)"
              />
            </ListCell>
          </ListRow>
        </ListRows>
      </List>
    </div>
    <Button v-if="ledger.hasMore" class="mt-3" label="Load more" @click="limit += 50" />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Avatar, Button, Select, TabButtons, dialog, toast } from 'frappe-ui'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import AppHeader from '@/components/AppHeader.vue'
import { revokeEntry, useContributors, useLedger } from '@/api'
import { SOURCES } from '@/utils/sources'
import { actionMeta } from '@/utils/actions'
import { formatDate } from '@/utils/dates'

const source = ref('all')
const login = ref(null)
const limit = ref(50)

const sourceOptions = [{ value: 'all', label: 'All' }, ...SOURCES.map((s) => ({ value: s.value, label: s.label }))]
const contributors = useContributors()
const contributorOptions = computed(() =>
  (contributors.data ?? []).map((p) => ({ label: p.fullName, value: p.login })),
)
const ledgerResource = useLedger({ login, source, limit })
const ledger = computed(() => ledgerResource.data ?? { rows: [], hasMore: false })

watch([source, login], () => (limit.value = 50))

function revoke(row) {
  dialog.prompt({
    title: 'Revoke these points?',
    message: `Adds a −${row.points} row for ${row.person.fullName}. The original row stays for the record.`,
    fields: [{ name: 'reason', label: 'Reason', required: true, placeholder: 'e.g. Spam PR, reverted later' }],
    confirmLabel: 'Revoke',
    theme: 'red',
    onConfirm: async ({ values }) => {
      await revokeEntry(row.id, values.reason)
      toast.success('Points revoked')
    },
  })
}
</script>
