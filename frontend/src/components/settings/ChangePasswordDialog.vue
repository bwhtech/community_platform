<template>
  <Dialog v-model:open="open" title="Change password">
    <form id="change-password-form" class="space-y-4" @submit.prevent="save">
      <Password v-model="current" label="Current password" autocomplete="current-password">
        <template #prefix>
          <span class="lucide-lock-keyhole size-4 text-ink-gray-4" aria-hidden="true" />
        </template>
      </Password>
      <Password v-model="next" label="New password" autocomplete="new-password">
        <template #prefix>
          <span class="lucide-lock-keyhole size-4 text-ink-gray-4" aria-hidden="true" />
        </template>
      </Password>
      <Password v-model="confirm" label="Confirm new password" autocomplete="new-password">
        <template #prefix>
          <span class="lucide-lock-keyhole size-4 text-ink-gray-4" aria-hidden="true" />
        </template>
      </Password>
    </form>
    <template #actions>
      <div class="flex items-center justify-between gap-2">
        <p class="text-sm" :class="message.ok ? 'text-ink-green-6' : 'text-ink-red-6'" aria-live="polite">
          {{ message.text }}
        </p>
        <Button
          variant="solid"
          type="submit"
          form="change-password-form"
          label="Update"
          :disabled="!message.ok"
          :loading="loading"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Button, Dialog, Password } from 'frappe-ui'
import { changePassword } from '@/api'
import { useAction } from '@/composables/useAction'

const open = defineModel('open', { type: Boolean })

const current = ref('')
const next = ref('')
const confirm = ref('')

// The server runs Frappe's own strength check too; this one gives instant feedback.
const STRONG = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d\s]).{8,}$/

const message = computed(() => {
  if (current.value && next.value && current.value === next.value)
    return { text: 'New password cannot be the same as current password' }
  if (next.value && next.value.length < 8) return { text: 'Password must be at least 8 characters' }
  if (next.value && !STRONG.test(next.value))
    return { text: 'Password must contain lowercase, uppercase, number, and symbol' }
  if (confirm.value && next.value !== confirm.value) return { text: 'Passwords do not match' }
  if (current.value && next.value && next.value === confirm.value) return { text: 'Passwords match', ok: true }
  return { text: '' }
})

const { run, loading } = useAction(changePassword, { success: 'Password updated' })

async function save() {
  if (!message.value.ok) return
  await run(current.value, next.value)
  open.value = false
}

watch(open, (isOpen) => {
  if (!isOpen) current.value = next.value = confirm.value = ''
})
</script>
