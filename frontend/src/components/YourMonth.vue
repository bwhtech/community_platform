<template>
  <div class="flex flex-wrap items-center gap-4 rounded-5 border border-outline-gray-1 p-4">
    <template v-if="!currentUser">
      <span class="lucide-sparkles size-5 text-ink-gray-5" aria-hidden="true" />
      <p class="min-w-0 flex-1 text-p-base text-ink-gray-7">
        Log in to see where you stand. Your past issues, PRs, talks and certifications count from day one.
      </p>
      <Button variant="solid" icon-left="lucide-log-in" label="Log in with GitHub" route="/login" />
    </template>

    <template v-else-if="me">
      <Avatar :label="me.fullName" :image="me.avatar" size="xl" />
      <div class="min-w-0 flex-1">
        <p class="flex items-center gap-2 text-base-semibold text-ink-gray-9">
          You're #{{ me.rank }} with {{ me.points.toLocaleString() }} points
          <RankChange :rank="me.rank" :previous-rank="me.previousRank" />
        </p>
        <p class="mt-1.5 text-p-sm text-ink-gray-6">
          <template v-if="me.ahead && gap === 0">
            Tied with {{ me.ahead.fullName }} at #{{ me.ahead.rank }}, who got there first.
          </template>
          <template v-else-if="me.ahead">
            {{ gap.toLocaleString() }} points behind {{ me.ahead.fullName }} at #{{ me.ahead.rank }}.
          </template>
          <template v-else>You're leading {{ monthLabel }}.</template>
          <template v-if="highlights(me.counts)">This month: {{ highlights(me.counts) }}.</template>
        </p>
      </div>
      <Button class="max-sm:hidden" label="Your profile" :route="`/u/${me.login}`" />
    </template>

    <template v-else>
      <span class="lucide-sprout size-5 text-ink-gray-5" aria-hidden="true" />
      <p class="min-w-0 flex-1 text-p-base text-ink-gray-7">
        No points for you in {{ monthLabel }} yet. Open an issue, get a PR merged or answer a question on Discuss.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Avatar, Button } from 'frappe-ui'
import RankChange from '@/components/RankChange.vue'
import { currentUser } from '@/session'
import { highlights } from '@/utils/actions'

const props = defineProps({
  board: { type: Object, required: true },
  monthLabel: { type: String, required: true },
})

const me = computed(() => props.board.me)
const gap = computed(() => me.value.ahead.points - me.value.points)
</script>
