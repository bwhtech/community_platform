<template>
  <AppHeader title="My profile" />

  <div class="flex flex-col items-center gap-3 px-3 py-24 text-center">
    <div class="rounded-full bg-surface-gray-2 p-3 text-ink-gray-5">
      <span class="lucide-user size-6" aria-hidden="true" />
    </div>
    <p class="text-lg-semibold text-ink-gray-8">
      {{ isLoggedIn ? 'Your account has no community profile' : 'Log in to see your profile' }}
    </p>
    <p class="max-w-sm text-p-base text-ink-gray-6">
      {{
        isLoggedIn
          ? `You're logged in as ${session.user}. Profiles are created when you log in with GitHub.`
          : 'Your profile collects your points, badges and activity across GitHub, Discuss, events and Frappe School.'
      }}
    </p>
    <Button
      v-if="!isLoggedIn"
      class="mt-2"
      variant="solid"
      icon-left="lucide-log-in"
      label="Log in with GitHub"
      :route="{ name: 'Login', query: { redirect: '/me' } }"
    />
  </div>
</template>

<script setup>
import { Button } from 'frappe-ui'
import AppHeader from '@/components/AppHeader.vue'
import { isLoggedIn, session } from '@/session'
</script>
