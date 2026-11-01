<template>
  <Dialog v-model:open="open" :title="request ? 'Edit feature request' : 'New feature request'" size="xl">
    <form id="request-form" class="space-y-4" @submit.prevent="save">
      <div v-if="restored" class="flex items-center justify-between gap-2 rounded-4 bg-surface-gray-2 py-1 pl-3 pr-1">
        <p class="text-p-sm text-ink-gray-7">Restored your unsaved draft.</p>
        <Button variant="ghost" size="sm" label="Discard" @click="discardDraft" />
      </div>
      <FormControl
        v-model="form.title"
        label="Title"
        placeholder="One line that says what you want"
        required
        :error="errors.title"
      />
      <FormControl
        v-model="form.product"
        type="select"
        label="Product"
        :options="productOptions"
        required
        :error="errors.product"
      />
      <DescriptionEditor
        v-model="form.description"
        placeholder="What are you trying to do, and what gets in the way?"
        description="Say what problem this solves for you."
        :error="errors.description"
      />
      <p v-if="!request" class="text-p-sm text-ink-gray-5">
        You can edit your request for 24 hours after you post it.
      </p>
    </form>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button label="Cancel" @click="open = false" />
        <Button
          variant="solid"
          type="submit"
          form="request-form"
          :loading="loading"
          :label="request ? 'Save' : 'Post request'"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, defineAsyncComponent, reactive, ref, watch } from 'vue'
import { Button, Dialog, FormControl } from 'frappe-ui'
import { createFeatureRequest, listProducts, updateFeatureRequest } from '@/api'
import { useAction } from '@/composables/useAction'
import { useDraft } from '@/composables/useDraft'
import { session } from '@/session'

// The editor is heavy, so it loads only when the dialog first opens.
const DescriptionEditor = defineAsyncComponent(() => import('@/components/requests/DescriptionEditor.vue'))

const props = defineProps({
  request: { type: Object, default: null },
  defaultProduct: { type: String, default: null },
})
const emit = defineEmits(['saved'])
const open = defineModel('open', { type: Boolean, default: false })

const form = reactive({ title: '', description: '', product: null })
const errors = reactive({})
const restored = ref(false)

// One draft per user and per request, so edits don't clobber a new post.
const draft = useDraft(() => `community:request-draft:${session.user}:${props.request?.id ?? 'new'}`)

const productOptions = computed(() => listProducts().map((p) => ({ label: p.name, value: p.id })))

const { run, loading } = useAction((values) =>
  props.request ? updateFeatureRequest(props.request.id, values) : createFeatureRequest(values),
)

function initial() {
  return {
    title: props.request?.title ?? '',
    description: props.request?.description ?? '',
    product: props.request?.product ?? props.defaultProduct,
  }
}

watch(open, (isOpen) => {
  if (!isOpen) return
  const saved = draft.load()
  restored.value = Boolean(saved)
  Object.assign(form, initial(), saved)
  Object.keys(errors).forEach((k) => delete errors[k])
})

// Keep the draft only while it differs from what the dialog opened with.
watch(form, () => {
  if (!open.value) return
  if (JSON.stringify(form) === JSON.stringify(initial())) draft.clear()
  else draft.save({ ...form })
})

function discardDraft() {
  draft.clear()
  restored.value = false
  Object.assign(form, initial())
}

function validate() {
  errors.title = form.title.trim().length < 8 ? 'Write at least 8 characters.' : null
  errors.product = form.product ? null : 'Pick a product.'
  errors.description = form.description.trim().length < 20 ? 'Write at least 20 characters.' : null
  return !errors.title && !errors.product && !errors.description
}

async function save() {
  if (!validate()) return
  const id = await run({ ...form })
  draft.clear()
  open.value = false
  emit('saved', id ?? props.request.id)
}
</script>
