<template>
  <Dialog v-model:open="open" :title="badge ? 'Edit badge' : 'New badge'" size="lg">
    <form id="badge-form" class="space-y-4" @submit.prevent="save">
      <div class="flex items-center gap-3">
        <BadgeIcon :badge="form" size="lg" />
        <div class="grid flex-1 grid-cols-2 gap-3">
          <FormControl v-model="form.icon" type="select" label="Icon" :options="ICONS" />
          <FormControl v-model="form.color" type="select" label="Color" :options="COLORS" />
        </div>
      </div>
      <FormControl v-model="form.title" label="Title" required :error="errors.title" />
      <FormControl v-model="form.description" type="textarea" label="Description" :rows="2" />
      <FormControl v-model="form.criteriaType" type="select" label="Awarded when" :options="CRITERIA" />

      <div v-if="form.criteriaType === 'action_count'" class="grid grid-cols-2 gap-3">
        <FormControl v-model="form.action" type="select" label="Action" :options="actionOptions" />
        <FormControl v-model="form.threshold" type="number" label="Count" description="1 makes it a “first …” badge." />
      </div>
      <FormControl
        v-if="form.criteriaType === 'points_total'"
        v-model="form.threshold"
        type="number"
        label="Points"
      />
      <FormControl
        v-if="form.criteriaType === 'monthly_rank'"
        v-model="form.rankLimit"
        type="number"
        label="Top N"
        description="Awarded on the 1st of each month for the month before."
      />
      <FormControl
        v-if="['action_count', 'monthly_rank'].includes(form.criteriaType)"
        v-model="form.product"
        type="select"
        label="Product"
        :options="productOptions"
      />
    </form>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button label="Cancel" @click="open = false" />
        <Button variant="solid" type="submit" form="badge-form" :loading="loading" label="Save" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { Button, Dialog, FormControl } from 'frappe-ui'
import BadgeIcon from '@/components/BadgeIcon.vue'
import { listProducts, saveBadge, usePointRules } from '@/api'
import { BADGE_ICONS } from '@/utils/badgeIcons'
import { useAction } from '@/composables/useAction'

const props = defineProps({ badge: { type: Object, default: null } })
const open = defineModel('open', { type: Boolean, default: false })

const CRITERIA = [
  { label: 'An action reaches a count', value: 'action_count' },
  { label: 'Total points reach a number', value: 'points_total' },
  { label: 'Monthly leaderboard rank', value: 'monthly_rank' },
  { label: 'An admin awards it', value: 'manual' },
]
const ICONS = BADGE_ICONS.map((icon) => ({ label: icon.replace('lucide-', ''), value: icon }))
const COLORS = ['gray', 'green', 'blue', 'violet', 'amber', 'red'].map((c) => ({ label: c, value: c }))
const BLANK = {
  id: null,
  title: '',
  description: '',
  icon: 'lucide-award',
  color: 'blue',
  criteriaType: 'action_count',
  action: 'github_pr_merged',
  threshold: 1,
  rankLimit: 3,
  product: '',
}

const form = reactive({ ...BLANK })
const errors = reactive({ title: null })

const rules = usePointRules()
const actionOptions = computed(() => (rules.data ?? []).map((r) => ({ label: r.label, value: r.action })))
const productOptions = computed(() => [
  { label: 'Any product', value: '' },
  ...listProducts().map((p) => ({ label: p.name, value: p.id })),
])

const { run, loading } = useAction(saveBadge, { success: 'Badge saved' })

watch(open, (isOpen) => {
  if (isOpen) Object.assign(form, BLANK, props.badge ?? {}, { product: props.badge?.product ?? '' })
  errors.title = null
})

async function save() {
  errors.title = form.title.trim() ? null : 'Give the badge a title.'
  if (errors.title) return
  await run({
    ...form,
    title: form.title.trim(),
    threshold: Number(form.threshold),
    rankLimit: Number(form.rankLimit),
    product: form.product || null,
  })
  open.value = false
}
</script>
