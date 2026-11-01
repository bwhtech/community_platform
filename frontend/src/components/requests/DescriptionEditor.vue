<template>
  <div class="space-y-1.5">
    <FormLabel :id="labelId" label="Description" required />
    <Editor v-model="model" format="markdown" :extensions="DESCRIPTION_EXTENSIONS" :placeholder="placeholder">
      <div
        class="rounded-4 border border-outline-gray-2 bg-surface-base hover:border-outline-gray-3 focus-within:border-outline-gray-4 focus-within:shadow-sm"
      >
        <EditorFixedMenu class="border-b border-outline-gray-1 px-1 py-1" :items="commentToolbar" size="sm" />
        <EditorContent
          class="prose-sm max-h-80 min-h-40 overflow-y-auto px-3 py-2 text-ink-gray-8"
          :aria-labelledby="labelId"
        />
      </div>
    </Editor>
    <ErrorMessage v-if="error" :message="error" />
    <p v-else-if="description" class="text-p-xs text-ink-gray-5">{{ description }}</p>
  </div>
</template>

<script setup>
import { useId } from 'vue'
import { ErrorMessage, FormLabel } from 'frappe-ui'
import { Editor, EditorContent, EditorFixedMenu, commentToolbar } from 'frappe-ui/editor'
import { DESCRIPTION_EXTENSIONS } from '@/utils/editor'

defineProps({
  placeholder: { type: String, default: '' },
  description: { type: String, default: '' },
  error: { type: String, default: null },
})
const model = defineModel({ type: String, default: '' })
const labelId = useId()
</script>
