<template>
  <AppHeader title="Badges" :back="currentUser ? `/u/${currentUser}` : '/leaderboard'">
    <template #actions>
      <span v-if="currentUser" class="text-sm text-ink-gray-5">{{ earnedCount }} of {{ badges.length }}</span>
    </template>
  </AppHeader>

  <div class="mx-auto max-w-[940px] px-3 pb-20 pt-5 sm:px-5">
    <p class="max-w-xl text-p-base text-ink-gray-6">
      Badges are awarded automatically as your contributions add up. Once earned, a badge stays on your
      profile for good.
    </p>
    <div class="mt-6 grid gap-3 sm:grid-cols-2">
      <div
        v-for="badge in badges"
        :key="badge.id"
        class="flex gap-4 rounded-5 border border-outline-gray-1 p-4"
      >
        <BadgeIcon :badge="badge" size="lg" :locked="Boolean(currentUser) && !badge.earnedByMe" />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h2 class="text-base-semibold text-ink-gray-8">{{ badge.title }}</h2>
            <Badge v-if="badge.earnedByMe" theme="green" label="Earned" size="sm" />
          </div>
          <p class="mt-1.5 text-p-sm text-ink-gray-6">{{ badge.description }}</p>
          <p class="mt-2 text-xs text-ink-gray-5">{{ badge.criteria }}</p>
          <div class="mt-3 flex items-center gap-2">
            <div class="flex gap-0.5">
              <RouterLink v-for="p in badge.recentEarners" :key="p.login" :to="`/u/${p.login}`">
                <Avatar :label="p.fullName" :image="p.avatar" size="sm" />
              </RouterLink>
            </div>
            <span class="text-xs text-ink-gray-5">
              {{ badge.earnedCount ? `Earned by ${badge.earnedCount}` : 'Not earned by anyone yet' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Avatar, Badge } from 'frappe-ui'
import AppHeader from '@/components/AppHeader.vue'
import BadgeIcon from '@/components/BadgeIcon.vue'
import { useBadges } from '@/api'
import { currentUser } from '@/session'

const badgesResource = useBadges()
const badges = computed(() => badgesResource.data ?? [])
const earnedCount = computed(() => badges.value.filter((b) => b.earnedByMe).length)
</script>
