<template>
  <AppHeader title="Point rules" />

  <div class="mx-auto max-w-[940px] px-3 pb-20 pt-5 sm:px-5">
    <Alert
      theme="blue"
      title="Changes apply to new activity only"
      description="Points already awarded are frozen in the ledger. Editing a rule does not change past totals or past leaderboards."
    />

    <div class="-mx-3 mt-6 overflow-x-auto">
      <List class="min-w-[40rem] list-row-px-3" :columns="['minmax(0,1fr)', '7rem', '6rem', '7rem', '4rem']">
        <ListHeader>
          <ListHeaderCell>Action</ListHeaderCell>
          <ListHeaderCell>Source</ListHeaderCell>
          <ListHeaderCell>Points</ListHeaderCell>
          <ListHeaderCell>Cap per item</ListHeaderCell>
          <ListHeaderCell class="justify-end">On</ListHeaderCell>
        </ListHeader>
        <ListRows :items="rules" row-key="action" v-slot="{ item }">
          <ListRow class="h-14">
            <ListCell class="gap-2.5">
              <span :class="actionMeta(item.action).icon" class="size-4 text-ink-gray-5" aria-hidden="true" />
              <span class="min-w-0">
                <span class="block truncate text-base text-ink-gray-8">{{ item.label }}</span>
                <span class="mt-1 block truncate font-mono text-xs text-ink-gray-4">{{ item.action }}</span>
              </span>
            </ListCell>
            <ListCell class="gap-1.5 text-sm text-ink-gray-7">
              <span :class="item.sourceInfo.icon" class="size-3.5 text-ink-gray-5" aria-hidden="true" />
              {{ item.sourceInfo.label }}
            </ListCell>
            <ListCell>
              <TextInput
                type="number"
                class="w-20"
                :model-value="item.points"
                :aria-label="`Points for ${item.label}`"
                @update:model-value="(v) => update(item, { points: toNumber(v) })"
              />
            </ListCell>
            <ListCell>
              <TextInput
                v-if="item.cap !== null"
                type="number"
                class="w-20"
                :model-value="item.cap"
                :aria-label="`Cap for ${item.label}`"
                @update:model-value="(v) => update(item, { cap: toNumber(v) })"
              />
              <span v-else class="text-sm text-ink-gray-4">—</span>
            </ListCell>
            <ListCell class="justify-end">
              <Switch
                :model-value="item.enabled"
                :aria-label="`Enable ${item.label}`"
                @update:model-value="(v) => update(item, { enabled: v })"
              />
            </ListCell>
          </ListRow>
        </ListRows>
      </List>
    </div>

    <p class="mt-4 text-p-sm text-ink-gray-5">
      Cap per item limits how many points one item can earn its author. For upvotes, a single feature request
      earns at most this many points.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Alert, Switch, TextInput, debounce, toast } from 'frappe-ui'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import AppHeader from '@/components/AppHeader.vue'
import { updatePointRule, usePointRules } from '@/api'
import { SOURCES } from '@/utils/sources'
import { actionMeta } from '@/utils/actions'

const rulesResource = usePointRules()
const rules = computed(() =>
  (rulesResource.data ?? []).map((r) => ({ ...r, sourceInfo: SOURCES.find((s) => s.value === r.source) })),
)

const notifySaved = debounce(() => toast.success('Point rules saved'), 600)

async function update(rule, patch) {
  if (Object.values(patch).some((v) => Number.isNaN(v))) return
  await updatePointRule(rule.action, patch)
  notifySaved()
}

function toNumber(value) {
  return value === '' ? NaN : Math.max(0, Math.round(Number(value)))
}
</script>
