<template>
  <div v-if="readonly" class="flex flex-wrap items-center justify-end gap-x-2 gap-y-1 text-sm text-ink-gray-5">
    <span v-for="r in shown" :key="r.emoji" class="whitespace-nowrap tabular-nums">{{ r.emoji }} {{ r.count }}</span>
  </div>
  <div v-else class="flex flex-wrap items-center gap-1.5">
    <Button
      v-for="r in shown"
      :key="r.emoji"
      size="sm"
      :variant="r.mine ? 'subtle' : 'outline'"
      :aria-pressed="r.mine"
      :aria-label="`React with ${r.emoji}`"
      @click="react(r.emoji)"
    >
      <span class="text-sm">{{ r.emoji }}</span>
      <span class="ml-1 text-sm tabular-nums text-ink-gray-7">{{ r.count }}</span>
    </Button>
    <Popover side="bottom" align="start">
      <template #trigger>
        <Button size="sm" variant="ghost" icon="lucide-smile-plus" aria-label="Add reaction" />
      </template>
      <template #default="{ close }">
        <div class="flex gap-0.5 p-1" role="group" aria-label="Reactions">
          <button
            v-for="r in request.reactions"
            :key="r.emoji"
            type="button"
            class="grid size-9 place-content-center rounded-4 text-xl transition-transform hover:scale-110 hover:bg-surface-gray-2"
            :class="{ 'bg-surface-blue-2': r.mine }"
            :aria-pressed="r.mine"
            :aria-label="r.mine ? `Remove ${r.emoji} reaction` : `React with ${r.emoji}`"
            @click="react(r.emoji), close()"
          >
            {{ r.emoji }}
          </button>
        </div>
      </template>
    </Popover>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button, Popover } from 'frappe-ui'
import { toggleReaction } from '@/api'
import { useAction } from '@/composables/useAction'
import { useRequireLogin } from '@/composables/useRequireLogin'

const props = defineProps({
  request: { type: Object, required: true },
  readonly: { type: Boolean, default: false },
})

const requireLogin = useRequireLogin()
const { run } = useAction(toggleReaction)

const shown = computed(() => props.request.reactions.filter((r) => r.count > 0))

function react(emoji) {
  if (!requireLogin()) return
  run(props.request.id, emoji)
}
</script>
