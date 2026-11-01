<template>
  <!-- Editor renders no element of its own; the div takes the parent's classes. -->
  <div>
    <Editor :model-value="source" format="markdown" :extensions="DESCRIPTION_EXTENSIONS" :editable="false">
      <EditorContent class="prose-sm text-ink-gray-8" />
    </Editor>
  </div>
</template>

<script setup>
import { Editor, EditorContent } from 'frappe-ui/editor'
import { DESCRIPTION_EXTENSIONS } from '@/utils/editor'

defineProps({ source: { type: String, default: '' } })
</script>
