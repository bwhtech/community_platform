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
      <div v-else class="h-screen w-full bg-surface-base text-ink-gray-9">
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
useColorScheme()
</script>
