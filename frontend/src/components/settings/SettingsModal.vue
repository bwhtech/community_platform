<template>
  <SettingsDialog v-model:open="settingsOpen" v-model:tab="settingsTab" size="4xl">
    <SettingsSidebar>
      <SettingsNavGroup label="Account">
        <SettingsNavItem value="profile">
          <template #prefix>
            <Avatar :label="me.fullName" :image="me.avatar" size="xs" />
          </template>
          My profile
        </SettingsNavItem>
      </SettingsNavGroup>
    </SettingsSidebar>

    <SettingsContent>
      <SettingsPanel value="profile">
        <ProfileSettings />
      </SettingsPanel>
    </SettingsContent>
  </SettingsDialog>
</template>

<script setup>
import { computed } from 'vue'
import {
  Avatar,
  SettingsContent,
  SettingsDialog,
  SettingsNavGroup,
  SettingsNavItem,
  SettingsPanel,
  SettingsSidebar,
} from 'frappe-ui'
import ProfileSettings from '@/components/settings/ProfileSettings.vue'
import { settingsOpen, settingsTab } from '@/composables/useSettings'
import { session } from '@/session'

const me = computed(() => session.me)
</script>
