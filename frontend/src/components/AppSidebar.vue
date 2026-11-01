<template>
  <Sidebar width="14rem" class="border-r">
    <SidebarHeader title="Frappe Community" subtitle="Frappeverse" logo="/assets/community_platform/logos/frappe.svg" />

    <div class="min-h-0 flex-1 space-y-0.5 overflow-y-auto px-2 pb-10 pt-0.5">
      <SidebarItem label="My profile" icon="lucide-user" route="/me" :active="isMyProfile" />
      <SidebarItem label="Leaderboard" icon="lucide-trophy" route="/leaderboard" />
      <SidebarItem label="Feature requests" icon="lucide-lightbulb" route="/requests" />

      <template v-if="isAdmin">
        <SidebarLabel class="pt-4">Admin</SidebarLabel>
        <SidebarItem label="Point rules" icon="lucide-coins" route="/admin/point-rules" />
        <SidebarItem label="Badges" icon="lucide-medal" route="/admin/badges" />
        <SidebarItem label="Products" icon="lucide-package" route="/admin/products" />
        <SidebarItem label="Point ledger" icon="lucide-scroll-text" route="/admin/ledger" />
      </template>
    </div>

    <div class="border-t border-outline-gray-1 p-2">
      <Dropdown v-if="isLoggedIn" :options="userOptions">
        <button
          type="button"
          class="flex w-full items-center gap-2 rounded-4 p-1.5 text-left hover:bg-surface-gray-2"
        >
          <Avatar :label="me?.fullName ?? session.user" :image="me?.avatar" size="sm" />
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm text-ink-gray-8">{{ me?.fullName ?? session.user }}</span>
            <span v-if="me" class="block truncate text-xs text-ink-gray-5">@{{ me.login }}</span>
          </span>
        </button>
      </Dropdown>
      <div v-else class="flex gap-1">
        <Button variant="solid" class="flex-1" icon-left="lucide-log-in" label="Log in with GitHub" @click="login()" />
        <Dropdown :options="[themeOption]">
          <Button variant="ghost" :icon="themeOption.icon" aria-label="Theme" />
        </Dropdown>
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Avatar,
  Button,
  Dropdown,
  Sidebar,
  SidebarHeader,
  SidebarItem,
  SidebarLabel,
  useColorScheme,
} from 'frappe-ui'
import { openSettings } from '@/composables/useSettings'
import { currentUser, isAdmin, isLoggedIn, login, logout, session } from '@/session'
import { THEMES } from '@/utils/theme'

const route = useRoute()
const { colorScheme, setColorScheme } = useColorScheme()

const me = computed(() => session.me)
const isMyProfile = computed(() => route.path === '/me' || route.path === `/u/${currentUser.value}`)

const themeOption = computed(() => ({
  label: 'Theme',
  icon: THEMES.find((t) => t.value === colorScheme.value)?.icon,
  submenu: THEMES.map((t) => ({
    label: t.label,
    icon: t.value === colorScheme.value ? 'lucide-check' : null,
    onClick: () => setColorScheme(t.value),
  })),
}))

// A desk user without a Contributor has nothing to edit in Settings.
const userOptions = computed(() => [
  me.value && { label: 'Settings', icon: 'lucide-settings', onClick: () => openSettings() },
  isAdmin.value && { label: 'Open Desk', icon: 'lucide-layout-dashboard', onClick: () => window.open('/app', '_blank') },
  themeOption.value,
  { label: 'Log out', icon: 'lucide-log-out', onClick: () => logout() },
].filter(Boolean))
</script>
