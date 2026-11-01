<template>
  <aside>
    <div class="flex items-center gap-4 lg:block">
      <Avatar :label="profile.fullName" :image="profile.avatar" size="3xl" class="!size-16 !text-2xl lg:!size-24 lg:!text-3xl" />
      <div class="min-w-0">
        <h1 class="truncate text-2xl font-semibold text-ink-gray-9 lg:mt-4 lg:text-3xl lg:font-semibold">{{ profile.fullName }}</h1>
        <p class="mt-1 text-lg text-ink-gray-5">@{{ profile.login }}</p>
      </div>
    </div>
    <p v-if="profile.bio" class="mt-4 text-p-base text-ink-gray-7">{{ profile.bio }}</p>
    <slot name="after-bio" />

    <ul class="mt-4 space-y-2 text-sm text-ink-gray-7">
      <li v-for="item in details" :key="item.icon" class="flex items-center gap-2">
        <span :class="item.icon" class="size-4 shrink-0 text-ink-gray-5" aria-hidden="true" />
        <a v-if="item.href" :href="item.href" target="_blank" rel="noopener" class="truncate hover:underline">
          {{ item.label }}
        </a>
        <span v-else class="truncate">{{ item.label }}</span>
      </li>
    </ul>

    <ul class="mt-4 space-y-2 border-t border-outline-gray-1 pt-4 text-sm text-ink-gray-7">
      <li v-for="link in links" :key="link.label" class="flex items-center gap-2">
        <span :class="link.icon" class="size-4 shrink-0 text-ink-gray-5" aria-hidden="true" />
        <a :href="link.href" target="_blank" rel="noopener" class="truncate hover:underline">{{ link.label }}</a>
      </li>
    </ul>

    <div v-if="products.length" class="mt-6">
      <h2 class="text-sm text-ink-gray-5">Works with</h2>
      <div class="mt-2 flex flex-wrap gap-1.5">
        <span
          v-for="p in products"
          :key="p.id"
          class="inline-flex items-center gap-1.5 rounded-full border border-outline-gray-1 py-1 pl-1.5 pr-2.5 text-sm text-ink-gray-7"
        >
          <ProductLogo :product="p" />
          {{ p.name }}
        </span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { Avatar } from 'frappe-ui'
import ProductLogo from '@/components/ProductLogo.vue'
import { getProduct } from '@/api'
import { formatDate } from '@/utils/dates'

const props = defineProps({ profile: { type: Object, required: true } })

const details = computed(() => {
  const p = props.profile
  return [
    p.company && { icon: 'lucide-building-2', label: p.company },
    p.location && { icon: 'lucide-map-pin', label: p.location },
    p.website && { icon: 'lucide-link', label: p.website.replace(/^https?:\/\//, ''), href: p.website },
    { icon: 'lucide-calendar', label: `Joined ${formatDate(p.joinedOn)}` },
  ].filter(Boolean)
})

const links = computed(() => {
  const p = props.profile
  return [
    { icon: 'lucide-code-xml', label: `GitHub · ${p.login}`, href: `https://github.com/${p.login}` },
    p.discussUsername && {
      icon: 'lucide-messages-square',
      label: `Discuss · ${p.discussUsername}`,
      href: `https://discuss.frappe.io/u/${p.discussUsername}`,
    },
    p.x && { icon: 'lucide-at-sign', label: `X · ${p.x}`, href: `https://x.com/${p.x}` },
    p.linkedin && { icon: 'lucide-briefcase-business', label: 'LinkedIn', href: `https://linkedin.com/in/${p.linkedin}` },
    p.youtube && { icon: 'lucide-circle-play', label: 'YouTube', href: `https://youtube.com/${p.youtube}` },
  ].filter(Boolean)
})

const products = computed(() => props.profile.products.map(getProduct).filter(Boolean))
</script>
