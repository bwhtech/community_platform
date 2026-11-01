<template>
  <div class="flex flex-col gap-1">
    <div class="flex gap-1">
      <!-- Day labels stay put while the weeks scroll on narrow screens. -->
      <div class="grid w-7 shrink-0 grid-rows-7 pt-5 text-xs text-ink-gray-5" :style="{ gap: `${GAP}px` }">
        <span
          v-for="(d, i) in DAY_LABELS"
          :key="i"
          class="leading-none"
          :style="{ height: `${CELL}px` }"
        >
          {{ d }}
        </span>
      </div>
      <div ref="scroller" class="min-w-0 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        <div class="inline-flex flex-col gap-1">
          <div class="relative h-4 text-xs text-ink-gray-5">
            <span
              v-for="m in monthLabels"
              :key="m.key"
              class="absolute"
              :style="{ left: `${m.week * STEP}px` }"
            >
              {{ m.label }}
            </span>
          </div>
          <div class="grid grid-flow-col grid-rows-7 p-0.5" :style="{ gap: `${GAP}px` }">
            <template v-for="day in days" :key="day.date">
              <button
                v-if="day.inRange"
                type="button"
                class="rounded-[2px] outline-offset-1"
                :class="[levelClass(day.count), { 'ring-2 ring-outline-gray-6 ring-offset-1': day.date === selected }]"
                :style="{ width: `${CELL}px`, height: `${CELL}px` }"
                :title="`${day.count} contribution${day.count === 1 ? '' : 's'} on ${formatDate(day.date)}`"
                :aria-label="`${day.count} contributions on ${formatDate(day.date)}`"
                @click="emit('select', day.date === selected ? null : day.date)"
              />
              <span v-else :style="{ width: `${CELL}px`, height: `${CELL}px` }" />
            </template>
          </div>
        </div>
      </div>
    </div>
    <div class="ml-8 mt-1 flex items-center justify-between gap-4 text-xs text-ink-gray-5">
      <span>{{ total }} contributions</span>
      <span class="flex shrink-0 items-center gap-1">
        Less
        <span
          v-for="level in [0, 1, 2, 4, 6]"
          :key="level"
          class="shrink-0 rounded-[2px]"
          :class="levelClass(level)"
          :style="{ width: `${CELL}px`, height: `${CELL}px` }"
        />
        More
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { addDays, dayOfWeek, formatDate } from '@/utils/dates'

const props = defineProps({
  start: { type: String, required: true },
  end: { type: String, required: true },
  counts: { type: Object, required: true },
  total: { type: Number, default: 0 },
  selected: { type: String, default: null },
})
const emit = defineEmits(['select'])

const scroller = ref(null)

// On narrow screens the grid overflows; start at the latest weeks.
watch(
  () => [props.start, props.end],
  async () => {
    await nextTick()
    if (scroller.value) scroller.value.scrollLeft = scroller.value.scrollWidth
  },
  { immediate: true },
)

const CELL = 10
const GAP = 2
const STEP = CELL + GAP
const DAY_LABELS = ['', 'Mon', '', 'Wed', '', 'Fri', '']
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

// Columns are weeks starting on Sunday, so the grid begins on the Sunday
// on or before `start` and pads out to the Saturday after `end`.
const days = computed(() => {
  const first = addDays(props.start, -dayOfWeek(props.start))
  const last = addDays(props.end, 6 - dayOfWeek(props.end))
  const out = []
  for (let d = first; d <= last; d = addDays(d, 1)) {
    out.push({ date: d, count: props.counts[d] ?? 0, inRange: d >= props.start && d <= props.end })
  }
  return out
})

const monthLabels = computed(() => {
  const labels = []
  days.value.forEach((day, i) => {
    if (day.inRange && (day.date.endsWith('-01') || i === 0)) {
      const week = Math.floor(i / 7)
      if (labels.length && week - labels.at(-1).week < 3) labels.pop()
      labels.push({ key: day.date, week, label: MONTHS[Number(day.date.slice(5, 7)) - 1] })
    }
  })
  return labels
})

function levelClass(count) {
  if (count === 0) return 'bg-surface-gray-2'
  if (count === 1) return 'bg-surface-blue-3'
  if (count <= 3) return 'bg-surface-blue-5'
  if (count <= 5) return 'bg-surface-blue-7'
  return 'bg-surface-blue-9'
}
</script>
