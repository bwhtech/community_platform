<template>
  <AppHeader :title="profile ? profile.fullName : 'Profile'">
    <template #actions>
      <div class="flex gap-2">
        <Button icon-left="lucide-share-2" label="Copy link" @click="copyLink" />
        <Button v-if="isMine" variant="solid" icon-left="lucide-pencil" label="Edit profile" @click="openSettings()" />
      </div>
    </template>
    <template #mobile-actions>
      <Button variant="ghost" icon="lucide-share-2" aria-label="Copy link" @click="copyLink" />
      <Button v-if="isMine" variant="ghost" icon="lucide-pencil" aria-label="Edit profile" @click="openSettings()" />
    </template>
  </AppHeader>

  <div
    v-if="!profile && !profileResource.isFinished"
    class="mx-auto flex max-w-[1080px] flex-col gap-8 px-3 pt-6 sm:px-5 lg:flex-row"
    aria-busy="true"
  >
    <div class="lg:w-[17rem] lg:shrink-0">
      <div class="flex items-center gap-4 lg:block">
        <Skeleton class="size-16 shrink-0 rounded-full lg:size-24" />
        <div class="space-y-2 lg:mt-4">
          <Skeleton class="h-7 w-44 rounded-2" />
          <Skeleton class="h-5 w-28 rounded-2" />
        </div>
      </div>
      <div class="mt-4 space-y-2">
        <Skeleton class="h-4 w-full rounded-2" />
        <Skeleton class="h-4 w-4/5 rounded-2" />
      </div>
      <div class="mt-4 space-y-3">
        <Skeleton v-for="i in 3" :key="i" class="h-4 w-36 rounded-2" />
      </div>
    </div>
    <div class="min-w-0 flex-1 space-y-8">
      <Skeleton class="h-[5.5rem] rounded-5" />
      <div>
        <Skeleton class="h-5 w-24 rounded-2" />
        <div class="mt-3 flex flex-wrap gap-2">
          <Skeleton v-for="i in 4" :key="i" class="h-8 w-28 rounded-full" />
        </div>
      </div>
      <div>
        <Skeleton class="h-5 w-32 rounded-2" />
        <Skeleton class="mt-4 h-40 rounded-5" />
      </div>
    </div>
  </div>

  <div v-else-if="!profile" class="flex flex-col items-center gap-3 py-24 text-center">
    <div class="rounded-full bg-surface-gray-2 p-3 text-ink-gray-5">
      <span class="lucide-user-x size-6" aria-hidden="true" />
    </div>
    <p class="text-base text-ink-gray-7">No one here goes by @{{ login }}</p>
    <Button label="Back to leaderboard" route="/leaderboard" />
  </div>

  <div v-else class="mx-auto flex max-w-[1080px] flex-col gap-8 px-3 pb-20 pt-6 sm:px-5 lg:flex-row">
    <ProfileAside :profile="profile" class="lg:w-[17rem] lg:shrink-0">
      <template v-if="isMobile" #after-bio>
        <div id="profile-contributions-mobile" class="mt-6" />
      </template>
    </ProfileAside>

    <div class="min-w-0 flex-1 space-y-8">
      <div class="grid grid-cols-2 divide-outline-gray-2 rounded-5 border border-outline-gray-1 sm:grid-cols-4 sm:divide-x">
        <div v-for="kpi in kpis" :key="kpi.label" class="px-4 py-3">
          <p class="text-sm text-ink-gray-5">{{ kpi.label }}</p>
          <p class="mt-2 text-2xl font-semibold tabular-nums text-ink-gray-9">{{ kpi.value }}</p>
          <p v-if="kpi.hint" class="mt-1 text-xs text-ink-gray-5">{{ kpi.hint }}</p>
        </div>
      </div>

      <section>
        <div class="flex items-center justify-between">
          <h2 class="text-lg-semibold text-ink-gray-8">Badges</h2>
          <Button variant="ghost" label="All badges" icon-right="lucide-arrow-right" route="/badges" />
        </div>
        <div v-if="badges.length" class="mt-3 flex flex-wrap gap-2">
          <Tooltip
            v-for="badge in badges"
            :key="badge.key"
            :text="`${badge.title}${badge.period ? ` · ${formatMonth(badge.period)}` : ''} — earned ${formatDate(badge.awardedOn)}`"
          >
            <div class="flex items-center gap-2 rounded-full border border-outline-gray-1 py-1 pl-1 pr-3">
              <BadgeIcon :badge="badge" size="sm" />
              <span class="text-sm text-ink-gray-7">{{ badge.title }}</span>
              <span v-if="badge.times > 1" class="text-xs tabular-nums text-ink-gray-5">×{{ badge.times }}</span>
            </div>
          </Tooltip>
        </div>
        <p v-else class="mt-3 text-sm text-ink-gray-5">No badges yet.</p>
      </section>

      <!-- On phones the heatmap moves up under the bio, ahead of the details. -->
      <Teleport defer to="#profile-contributions-mobile" :disabled="!isMobile">
        <section>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <h2 class="text-lg-semibold text-ink-gray-8">Contributions</h2>
            <div class="flex items-center gap-2">
              <TabButtons v-if="!isMobile" v-model="source" :options="sourceOptions" />
              <div v-else class="w-32">
                <Select v-model="source" :options="sourceOptions" />
              </div>
              <div class="w-36">
                <Select v-model="range" :options="rangeOptions" />
              </div>
            </div>
          </div>
          <div class="mt-4 rounded-5 border border-outline-gray-1 p-4">
            <ContributionHeatmap
              v-if="heatmap"
              v-bind="heatmap"
              :selected="selectedDay"
              @select="selectedDay = $event"
            />
          </div>
        </section>
      </Teleport>

      <section>
        <div class="flex items-center justify-between">
          <h2 class="text-lg-semibold text-ink-gray-8">
            {{ selectedDay ? `Activity on ${formatDate(selectedDay)}` : 'Recent activity' }}
          </h2>
          <Button v-if="selectedDay" variant="ghost" icon-left="lucide-x" label="Clear day" @click="selectedDay = null" />
        </div>
        <ActivityList v-if="activity" class="mt-2" :rows="activity.rows" />
      </section>

      <section class="grid gap-8 sm:grid-cols-2">
        <div>
          <h2 class="text-lg-semibold text-ink-gray-8">Talks and events</h2>
          <ul class="mt-3 space-y-3">
            <li v-for="talk in profile.talks" :key="talk.id" class="flex gap-2">
              <span class="lucide-mic mt-0.5 size-4 shrink-0 text-ink-violet-6" aria-hidden="true" />
              <span class="min-w-0">
                <span class="block text-p-sm text-ink-gray-8">{{ talk.title }}</span>
                <span class="mt-1 block text-xs text-ink-gray-5">Speaker · {{ formatDate(talk.date) }}</span>
              </span>
            </li>
            <li v-for="event in profile.eventsAttended" :key="event.id" class="flex gap-2">
              <span class="lucide-ticket mt-0.5 size-4 shrink-0 text-ink-gray-5" aria-hidden="true" />
              <span class="min-w-0">
                <span class="block text-p-sm text-ink-gray-8">{{ event.title }}</span>
                <span class="mt-1 block text-xs text-ink-gray-5">Attended · {{ formatDate(event.date) }}</span>
              </span>
            </li>
          </ul>
          <p v-if="!profile.talks.length && !profile.eventsAttended.length" class="mt-3 text-sm text-ink-gray-5">
            No events yet. Records come from events.frappe.io.
          </p>
        </div>
        <div>
          <h2 class="text-lg-semibold text-ink-gray-8">Certifications</h2>
          <ul class="mt-3 space-y-3">
            <li v-for="cert in profile.certifications" :key="cert.id" class="flex gap-2">
              <span class="lucide-graduation-cap mt-0.5 size-4 shrink-0 text-ink-green-6" aria-hidden="true" />
              <span class="min-w-0">
                <a :href="cert.url" target="_blank" rel="noopener" class="block text-p-sm text-ink-gray-8 hover:underline">
                  {{ cert.title }}
                </a>
                <span class="mt-1 block text-xs text-ink-gray-5">Frappe School · {{ formatDate(cert.date) }}</span>
              </span>
            </li>
          </ul>
          <p v-if="!profile.certifications.length" class="mt-3 text-sm text-ink-gray-5">
            No certifications yet. Records come from school.frappe.io.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Button, Select, Skeleton, TabButtons, Tooltip, toast } from 'frappe-ui'
import AppHeader from '@/components/AppHeader.vue'
import ActivityList from '@/components/ActivityList.vue'
import BadgeIcon from '@/components/BadgeIcon.vue'
import ContributionHeatmap from '@/components/ContributionHeatmap.vue'
import ProfileAside from '@/components/ProfileAside.vue'
import { useActivity, useHeatmap, useProfile } from '@/api'
import { SOURCES } from '@/utils/sources'
import { useIsMobile } from '@/composables/useIsMobile'
import { openSettings } from '@/composables/useSettings'
import { currentUser } from '@/session'
import { formatDate, formatMonth } from '@/utils/dates'

const RECENT_LIMIT = 7

const props = defineProps({ login: { type: String, required: true } })

const isMobile = useIsMobile()
const source = ref('all')
const range = ref('last')
const selectedDay = ref(null)

const login = computed(() => props.login)
const profileResource = useProfile(login)
const profile = computed(() => profileResource.data)
const isMine = computed(() => props.login === currentUser.value)

const sourceOptions = [{ value: 'all', label: 'All' }, ...SOURCES.map((s) => ({ value: s.value, label: s.label }))]
const rangeOptions = computed(() => [
  { label: 'Last 12 months', value: 'last' },
  ...(profile.value?.heatmapYears ?? []).map((y) => ({ label: String(y), value: String(y) })),
])

const heatmapResource = useHeatmap(login, range, source)
const heatmap = computed(() => heatmapResource.data)

// A picked day shows everything from that day; otherwise just the latest few.
const activityResource = useActivity(login, {
  source,
  date: selectedDay,
  limit: computed(() => (selectedDay.value ? 500 : RECENT_LIMIT)),
})
const activity = computed(() => activityResource.data)

watch([source, range], () => (selectedDay.value = null))

const kpis = computed(() => {
  const p = profile.value
  return [
    { label: 'Total points', value: p.totalPoints.toLocaleString(), hint: p.overallRank ? `#${p.overallRank} all time` : null },
    { label: 'This month', value: p.monthPoints.toLocaleString(), hint: p.monthRank ? `#${p.monthRank} overall` : 'Not ranked yet' },
    { label: 'PRs merged', value: p.stats.prsMerged, hint: `${p.stats.reviews} reviews · ${p.stats.issuesOpened} issues` },
    { label: 'Discuss solutions', value: p.stats.solutions, hint: p.discussUsername ? `@${p.discussUsername}` : 'Not connected' },
  ]
})

// Monthly-rank badges can be earned many times; show each badge once with a count.
const badges = computed(() => {
  const grouped = new Map()
  for (const badge of profile.value?.badges ?? []) {
    const entry = grouped.get(badge.id)
    if (entry) entry.times++
    else grouped.set(badge.id, { ...badge, key: badge.id, times: 1 })
  }
  return [...grouped.values()]
})

function copyLink() {
  navigator.clipboard.writeText(window.location.href)
  toast.success('Profile link copied')
}
</script>
