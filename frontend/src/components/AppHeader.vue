<template>
  <PageHeaderMobile v-if="isMobile">
    <template v-if="back" #prefix>
      <PageHeaderBackButton :fallback-route="back" />
    </template>
    <PageHeaderMobileTitle :title="title" />
    <template v-if="$slots['mobile-actions'] || $slots.actions" #suffix>
      <slot name="mobile-actions"><slot name="actions" /></slot>
    </template>
  </PageHeaderMobile>
  <PageHeader v-else>
    <slot name="title"><PageHeaderTitle :title="title" /></slot>
    <slot name="actions" />
  </PageHeader>
</template>

<script setup>
import {
  PageHeader,
  PageHeaderBackButton,
  PageHeaderMobile,
  PageHeaderMobileTitle,
  PageHeaderTitle,
} from 'frappe-ui'
import { useIsMobile } from '@/composables/useIsMobile'

// One header for both shells. `#actions` shows on both unless the page
// passes a tighter `#mobile-actions`; `back` adds a back button on mobile.
defineProps({
  title: { type: String, required: true },
  back: { type: [String, Object], default: null },
})

const isMobile = useIsMobile()
</script>
