<template>
  <FrappeUIProvider>
    <router-view v-if="route.name === 'Login'" />
    <template v-else>
      <MobileShell v-if="isMobile" class="bg-surface-base text-ink-gray-9">
        <router-view :key="route.path" />
        <template #nav>
          <AppMobileNav />
        </template>
      </MobileShell>
      <div v-else class="h-dvh w-full bg-surface-base text-ink-gray-9">
        <DesktopShell>
          <template #sidebar>
            <AppSidebar />
          </template>
          <router-view :key="route.path" />
        </DesktopShell>
      </div>
      <SettingsModal v-if="currentUser" />
    </template>
  </FrappeUIProvider>
</template>

<script setup>
import { watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { DesktopShell, FrappeUIProvider, MobileShell, useColorScheme } from 'frappe-ui'
import AppMobileNav from '@/components/AppMobileNav.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import SettingsModal from '@/components/settings/SettingsModal.vue'
import { useIsMobile } from '@/composables/useIsMobile'
import { currentUser } from '@/session'

const route = useRoute()
const isMobile = useIsMobile()

// Restores the saved theme, or follows the OS setting when none is saved.
const { resolvedColorScheme } = useColorScheme()

// The status bar reads theme-color, which only knows the OS scheme. Repaint
// every tag with the scheme the page is in, so a saved override matches too.
const THEME_COLORS = { light: '#ffffff', dark: '#171717' }
watchEffect(() => {
  for (const meta of document.querySelectorAll('meta[name="theme-color"]')) {
    meta.content = THEME_COLORS[resolvedColorScheme.value]
  }
})
</script>
