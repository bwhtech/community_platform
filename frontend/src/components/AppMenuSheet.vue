<template>
  <BottomSheet v-model:open="open" title="Menu">
    <div class="space-y-6 px-4 pb-8 pt-2">
      <div v-if="me" class="flex items-center gap-3">
        <Avatar :label="me.fullName" :image="me.avatar" size="xl" />
        <div class="min-w-0 flex-1">
          <p class="truncate text-lg-semibold text-ink-gray-9">{{ me.fullName }}</p>
          <p class="mt-1 truncate text-md text-ink-gray-5">@{{ me.login }}</p>
        </div>
      </div>
      <Button
        v-else-if="!isLoggedIn"
        class="w-full"
        size="md"
        variant="solid"
        icon-left="lucide-log-in"
        label="Log in with GitHub"
        @click="go(login)"
      />

      <div v-if="isLoggedIn" class="space-y-1">
        <Button v-if="me" class="w-full !justify-start" size="md" variant="ghost" icon-left="lucide-settings" label="Settings" @click="go(openSettings)" />
        <template v-if="isAdmin">
          <p class="px-2 pt-3 text-sm text-ink-gray-5">Admin</p>
          <Button
            v-for="link in ADMIN_LINKS"
            :key="link.route"
            class="w-full !justify-start"
            size="md"
            variant="ghost"
            :icon-left="link.icon"
            :label="link.label"
            @click="go(() => router.push(link.route))"
          />
        </template>
      </div>

      <div class="space-y-2">
        <p class="text-sm text-ink-gray-5">Theme</p>
        <TabButtons
          :model-value="colorScheme"
          :options="THEMES.map((t) => ({ value: t.value, label: t.label, iconLeft: t.icon }))"
          fluid
          @update:model-value="setColorScheme"
        />
      </div>

      <Button
        v-if="isLoggedIn"
        class="w-full"
        size="md"
        theme="red"
        icon-left="lucide-log-out"
        label="Log out"
        @click="go(logout)"
      />
    </div>
  </BottomSheet>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Avatar, BottomSheet, Button, TabButtons, useColorScheme } from 'frappe-ui'
import { openSettings } from '@/composables/useSettings'
import { isAdmin, isLoggedIn, login, logout, session } from '@/session'
import { THEMES } from '@/utils/theme'

const ADMIN_LINKS = [
  { label: 'Point rules', icon: 'lucide-coins', route: '/admin/point-rules' },
  { label: 'Badges', icon: 'lucide-medal', route: '/admin/badges' },
  { label: 'Products', icon: 'lucide-package', route: '/admin/products' },
  { label: 'Point ledger', icon: 'lucide-scroll-text', route: '/admin/ledger' },
]

const open = defineModel('open', { type: Boolean, default: false })
const router = useRouter()
const { colorScheme, setColorScheme } = useColorScheme()

const me = computed(() => session.me)

function go(action) {
  open.value = false
  action()
}
</script>
