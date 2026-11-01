<template>
  <MobileNav>
    <MobileNavItem label="Leaderboard" icon="lucide-trophy" route="/leaderboard" />
    <MobileNavItem label="Requests" icon="lucide-lightbulb" route="/requests" />
    <MobileNavItem label="You" route="/me" :active="isMyProfile">
      <template #default="{ active }">
        <Avatar
          v-if="me"
          :label="me.fullName"
          :image="me.avatar"
          size="sm"
          :class="{ 'ring-2 ring-outline-gray-5 ring-offset-1': active }"
        />
        <span v-else class="lucide-user size-5" aria-hidden="true" />
      </template>
    </MobileNavItem>
    <MobileNavItem label="Menu" icon="lucide-menu" @click="menuOpen = true" />
  </MobileNav>
  <AppMenuSheet v-model:open="menuOpen" />
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Avatar, MobileNav, MobileNavItem } from 'frappe-ui'
import AppMenuSheet from '@/components/AppMenuSheet.vue'
import { currentUser, session } from '@/session'

const route = useRoute()
const menuOpen = ref(false)

const me = computed(() => session.me)
const isMyProfile = computed(() => route.path === '/me' || route.path === `/u/${currentUser.value}`)
</script>
