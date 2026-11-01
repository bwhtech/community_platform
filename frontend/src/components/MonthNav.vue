<template>
  <div class="flex items-center gap-1">
    <Button
      variant="ghost"
      icon="lucide-chevron-left"
      aria-label="Previous month"
      :disabled="index === months.length - 1"
      @click="month = months[index + 1]"
    />
    <Select v-model="month" :options="options" />
    <Button
      variant="ghost"
      icon="lucide-chevron-right"
      aria-label="Next month"
      :disabled="index === 0"
      @click="month = months[index - 1]"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Button, Select } from 'frappe-ui'
import { formatMonth } from '@/utils/dates'

// `months` is newest first, so "previous" moves forward in the array.
const props = defineProps({ months: { type: Array, required: true } })
const month = defineModel({ type: String, required: true })

const index = computed(() => props.months.indexOf(month.value))
const options = computed(() => props.months.map((m) => ({ label: formatMonth(m), value: m })))
</script>
