<template>
  <AppHeader title="Badges">
    <template #actions>
      <Button variant="solid" icon-left="lucide-plus" label="New badge" @click="openDialog(null)" />
    </template>
    <template #mobile-actions>
      <Button variant="ghost" icon="lucide-plus" aria-label="New badge" @click="openDialog(null)" />
    </template>
  </AppHeader>

  <div class="mx-auto max-w-[940px] px-3 pb-20 pt-5 sm:px-5">
    <div class="-mx-3 overflow-x-auto">
      <List class="min-w-[36rem] list-row-px-3" :columns="['minmax(0,1fr)', 'minmax(0,16rem)', '5rem', '3rem']">
        <ListHeader>
          <ListHeaderCell>Badge</ListHeaderCell>
          <ListHeaderCell>Criteria</ListHeaderCell>
          <ListHeaderCell class="justify-end">Earned</ListHeaderCell>
          <ListHeaderCell />
        </ListHeader>
        <ListRows :items="badges" v-slot="{ item }">
          <ListRow class="py-3">
            <ListCell class="gap-3">
              <BadgeIcon :badge="item" size="sm" />
              <span class="min-w-0">
                <span class="block truncate text-base text-ink-gray-8">{{ item.title }}</span>
                <span class="mt-1 block truncate text-sm text-ink-gray-5">{{ item.description }}</span>
              </span>
            </ListCell>
            <ListCell class="text-sm text-ink-gray-7">
              <span class="truncate">{{ item.criteria }}</span>
            </ListCell>
            <ListCell class="justify-end tabular-nums text-ink-gray-7">{{ item.earnedCount }}</ListCell>
            <ListCell class="justify-end">
              <Dropdown :options="rowOptions(item)">
                <Button variant="ghost" icon="lucide-ellipsis" :aria-label="`Options for ${item.title}`" />
              </Dropdown>
            </ListCell>
          </ListRow>
        </ListRows>
      </List>
    </div>
  </div>

  <BadgeDialog v-model:open="showDialog" :badge="editing" />
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button, Dropdown, dialog, toast } from 'frappe-ui'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import AppHeader from '@/components/AppHeader.vue'
import BadgeDialog from '@/components/BadgeDialog.vue'
import BadgeIcon from '@/components/BadgeIcon.vue'
import { awardBadge, deleteBadge, useAdminBadges, useContributors } from '@/api'

const badgesResource = useAdminBadges()
const badges = computed(() => badgesResource.data ?? [])
const contributors = useContributors()
const showDialog = ref(false)
const editing = ref(null)

function openDialog(badge) {
  editing.value = badge && { ...badge }
  showDialog.value = true
}

function rowOptions(badge) {
  return [
    { label: 'Edit', icon: 'lucide-pencil', onClick: () => openDialog(badge) },
    { label: 'Award to someone', icon: 'lucide-user-plus', onClick: () => award(badge) },
    { label: 'Delete', icon: 'lucide-trash-2', theme: 'red', onClick: () => remove(badge) },
  ]
}

function award(badge) {
  dialog.prompt({
    title: `Award “${badge.title}”`,
    fields: [
      {
        name: 'login',
        label: 'Contributor',
        type: 'combobox',
        required: true,
        options: (contributors.data ?? []).map((p) => ({ label: `${p.fullName} (@${p.login})`, value: p.login })),
      },
    ],
    confirmLabel: 'Award',
    onConfirm: async ({ values }) => {
      await awardBadge(badge.id, values.login)
      toast.success('Badge awarded')
    },
  })
}

function remove(badge) {
  dialog.confirm({
    title: `Delete “${badge.title}”?`,
    message: `It is removed from the ${badge.earnedCount} profiles that earned it.`,
    confirmLabel: 'Delete',
    theme: 'red',
    onConfirm: async () => {
      await deleteBadge(badge.id)
      toast.success('Badge deleted')
    },
  })
}
</script>
