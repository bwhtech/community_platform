<template>
  <Tooltip :text="tooltip">
    <button
      type="button"
      class="relative flex shrink-0 flex-col items-center justify-center rounded-5 transition-[background-color,color,transform] duration-150 active:scale-95"
      :class="[
        large ? 'h-16 w-14 gap-1' : 'h-12 w-11 gap-0.5',
        request.upvoted
          ? 'bg-surface-blue-2 text-ink-blue-7 hover:bg-surface-blue-3'
          : 'bg-surface-gray-2 text-ink-gray-6 hover:bg-surface-gray-3 hover:text-ink-gray-8',
        { 'cursor-default active:scale-100': request.isMine },
      ]"
      :aria-pressed="request.upvoted"
      :aria-label="`Upvote, ${request.upvotes} votes`"
      :disabled="loading"
      @click="onClick"
    >
      <span class="lucide-arrow-big-up" :class="large ? 'size-5' : 'size-4'" aria-hidden="true" />
      <span class="tabular-nums" :class="large ? 'text-base-semibold' : 'text-sm-semibold'">{{ request.upvotes }}</span>
    </button>
  </Tooltip>
</template>

<script setup>
import { computed } from 'vue'
import { Tooltip } from 'frappe-ui'
import { toggleUpvote } from '@/api'
import { useAction } from '@/composables/useAction'
import { useRequireLogin } from '@/composables/useRequireLogin'

const props = defineProps({
  request: { type: Object, required: true },
  large: { type: Boolean, default: false },
})

const requireLogin = useRequireLogin()
const { run, loading } = useAction(toggleUpvote)

const tooltip = computed(() => {
  if (props.request.isMine) return 'Your request is upvoted automatically'
  return props.request.upvoted ? 'Remove upvote' : 'Upvote'
})

function onClick() {
  if (!requireLogin() || props.request.isMine) return
  run(props.request.id)
}
</script>
