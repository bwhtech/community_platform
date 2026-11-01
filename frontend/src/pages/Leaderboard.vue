<template>
  <AppHeader title="Leaderboard">
    <template #actions>
      <MonthNav v-if="!isMobile" v-model="month" :months="months" />
    </template>
  </AppHeader>

  <div class="mx-auto max-w-[940px] space-y-8 px-3 pb-20 pt-6 sm:px-5">
    <div>
      <MonthNav v-if="isMobile" class="-ml-2" v-model="month" :months="months" />
      <h1 v-else class="text-3xl font-semibold text-ink-gray-9">{{ formatMonth(month) }}</h1>
      <p class="mt-2 text-base text-ink-gray-5">{{ statusLine }}</p>
    </div>

    <div class="grid grid-cols-2 rounded-5 border border-outline-gray-1 sm:grid-cols-4 sm:divide-x sm:divide-outline-gray-2">
      <div v-for="kpi in kpis" :key="kpi.label" class="px-4 py-3">
        <p class="text-sm text-ink-gray-5">{{ kpi.label }}</p>
        <p class="mt-2 text-2xl font-semibold tabular-nums text-ink-gray-9">{{ kpi.value.toLocaleString() }}</p>
      </div>
    </div>

    <div v-if="podium.length === 3" class="grid grid-cols-3 items-end gap-2 sm:gap-3">
      <RouterLink
        v-for="row in podium"
        :key="row.login"
        :to="`/u/${row.login}`"
        class="flex flex-col items-center rounded-6 border px-3 text-center hover:bg-surface-gray-1"
        :class="row.rank === 1 ? 'border-outline-amber-3 py-4 shadow-sm sm:py-6' : 'border-outline-gray-1 py-3 sm:py-5'"
      >
        <span class="inline-flex items-center gap-1 text-sm-semibold" :class="MEDALS[row.rank].text">
          <span class="lucide-medal size-4" aria-hidden="true" />
          {{ MEDALS[row.rank].label }}
        </span>
        <Avatar class="mt-3" :label="row.fullName" :image="row.avatar" :size="isMobile ? 'xl' : row.rank === 1 ? '3xl' : '2xl'" />
        <span class="mt-3 w-full truncate text-base-semibold text-ink-gray-9 sm:text-lg-semibold">{{ row.fullName }}</span>
        <span class="mt-1 text-xl font-semibold tabular-nums text-ink-gray-9 sm:text-2xl">{{ row.points.toLocaleString() }}</span>
        <span class="text-xs text-ink-gray-5">points</span>
        <span class="mt-3 w-full truncate text-sm text-ink-gray-6 max-sm:hidden">{{ highlights(row.counts, 2) }}</span>
        <div class="mt-3 w-full max-w-36 max-sm:hidden">
          <SourceBar :by-source="row.bySource" />
        </div>
      </RouterLink>
    </div>

    <YourMonth v-if="!loading" :board="board" :month-label="formatMonth(month)" />

    <section v-if="rest.length">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h2 class="text-lg-semibold text-ink-gray-8">Everyone else</h2>
        <div class="flex flex-wrap items-center gap-3 text-xs text-ink-gray-5 max-md:hidden">
          <span v-for="s in SOURCES" :key="s.value" class="inline-flex items-center gap-1.5">
            <span class="size-2 rounded-full" :class="s.color" aria-hidden="true" />{{ s.label }}
          </span>
        </div>
      </div>
      <List class="-mx-3 mt-3 list-row-px-3" :columns="COLUMNS">
        <ListRows :items="rest" row-key="login" v-slot="{ item }">
          <LeaderboardRow :row="item" :is-me="item.login === currentUser" />
        </ListRows>
      </List>
    </section>

    <div v-if="loading" class="divide-y divide-outline-gray-1" aria-busy="true">
      <div v-for="i in 6" :key="i" class="flex h-16 items-center gap-3">
        <Skeleton class="h-4 w-6 rounded-2" />
        <Skeleton class="ml-3 size-8 shrink-0 rounded-full" />
        <div class="flex-1 space-y-2">
          <Skeleton class="h-4 w-40 rounded-2" />
          <Skeleton class="h-3 w-56 max-w-full rounded-2" />
        </div>
        <Skeleton class="h-5 w-12 rounded-2" />
      </div>
    </div>
    <div v-else-if="!board.rows.length" class="flex flex-col items-center gap-3 py-16 text-center">
      <div class="rounded-full bg-surface-gray-2 p-3 text-ink-gray-5">
        <span class="lucide-trophy size-6" aria-hidden="true" />
      </div>
      <p class="text-base text-ink-gray-7">No points yet in {{ formatMonth(month) }}</p>
    </div>

    <div v-if="pinnedMe" class="sticky bottom-2 sm:bottom-4 rounded-5 border border-outline-gray-2 bg-surface-base px-3 shadow-md">
      <List :columns="COLUMNS" divider="none">
        <LeaderboardRow :row="pinnedMe" is-me />
      </List>
    </div>

    <p v-if="!loading" class="text-p-sm text-ink-gray-5">
      Showing the top {{ Math.min(board.total, 50) }} of {{ board.total }} contributors. Months follow IST. Ties go to
      whoever reached the score first. Arrows compare with the month before.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Avatar, Skeleton } from 'frappe-ui'
import { List, ListRows } from 'frappe-ui/list'
import AppHeader from '@/components/AppHeader.vue'
import LeaderboardRow from '@/components/LeaderboardRow.vue'
import MonthNav from '@/components/MonthNav.vue'
import SourceBar from '@/components/SourceBar.vue'
import YourMonth from '@/components/YourMonth.vue'
import { leaderboardMonths, useLeaderboard, useMonthSummary } from '@/api'
import { useIsMobile } from '@/composables/useIsMobile'
import { useQueryParam } from '@/composables/useQueryParam'
import { SOURCES } from '@/utils/sources'
import { currentUser } from '@/session'
import { highlights } from '@/utils/actions'
import { formatMonth, todayIST } from '@/utils/dates'

const COLUMNS = { base: ['3rem', 'minmax(0,1fr)', '5.5rem'], md: ['3rem', 'minmax(0,1fr)', '10rem', '5.5rem'] }
const MEDALS = {
  1: { label: '1st', text: 'text-ink-amber-7' },
  2: { label: '2nd', text: 'text-ink-gray-6' },
  3: { label: '3rd', text: 'text-ink-orange-6' },
}

const months = leaderboardMonths()
const month = useQueryParam('month', months[0])
const isMobile = useIsMobile()

const boardResource = useLeaderboard(month)
const summaryResource = useMonthSummary(month)
const board = computed(() => boardResource.data ?? { rows: [], me: null, total: 0 })
const summary = computed(() => summaryResource.data ?? { points: 0, contributors: 0, prsMerged: 0, solutions: 0 })
const loading = computed(() => !boardResource.data)

const podium = computed(() => {
  const [first, second, third] = board.value.rows
  return third ? [second, first, third] : []
})
const rest = computed(() => board.value.rows.slice(3))

// Your own row stays visible even when you're outside the top 50.
const pinnedMe = computed(() => {
  const me = board.value.me
  return me && me.rank > board.value.rows.length ? me : null
})

const kpis = computed(() => [
  { label: 'Points earned', value: summary.value.points },
  { label: 'Contributors', value: summary.value.contributors },
  { label: 'PRs merged', value: summary.value.prsMerged },
  { label: 'Discuss solutions', value: summary.value.solutions },
])

const statusLine = computed(() => {
  const today = todayIST()
  if (month.value !== today.slice(0, 7)) return 'Final standings'
  const [y, m, d] = today.split('-').map(Number)
  const left = new Date(Date.UTC(y, m, 0)).getUTCDate() - d
  if (left === 0) return 'Last day of the month · standings update every hour'
  return `In progress · ${left} day${left === 1 ? '' : 's'} left · standings update every hour`
})
</script>
