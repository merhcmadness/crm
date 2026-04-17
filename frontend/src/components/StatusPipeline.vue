<template>
  <div class="flex items-stretch overflow-x-auto select-none border-b" style="min-height: 40px; background: #1a1a2e;">
    <!-- Main statuses as chevrons -->
    <template v-for="(status, i) in mainStatuses" :key="status.name">
      <button
        class="relative flex items-center justify-center py-2 text-xs font-medium transition-all cursor-pointer"
        :class="[
          i === 0 ? 'pl-4 pr-6' : 'pl-8 pr-6',
          isActive(status) ? 'text-white' : 'text-gray-400 hover:text-gray-200',
        ]"
        :style="isActive(status)
          ? { background: status.color, boxShadow: `0 0 0 1px ${status.color}` }
          : { background: 'transparent' }"
        @click="$emit('change', status.name)"
      >
        <!-- Left chevron notch -->
        <span
          v-if="i > 0"
          class="absolute left-0 top-0 h-full w-4 overflow-hidden"
          style="pointer-events: none;"
        >
          <span
            class="absolute -left-2 top-1/2 h-5 w-5 -translate-y-1/2 rotate-45"
            :style="isActive(status)
              ? { background: status.color, border: '1px solid rgba(255,255,255,0.1)' }
              : { background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)' }"
          />
        </span>

        <span class="relative z-10 whitespace-nowrap">{{ __(status.name) }}</span>

        <!-- Right chevron point -->
        <span
          v-if="i < mainStatuses.length - 1"
          class="absolute right-0 top-0 z-10 h-full w-4 overflow-hidden"
          style="pointer-events: none;"
        >
          <span
            class="absolute -right-2.5 top-1/2 h-5 w-5 -translate-y-1/2 rotate-45"
            :style="isActive(status)
              ? { background: status.color, border: '1px solid rgba(255,255,255,0.15)', borderBottom: 'none', borderLeft: 'none' }
              : { background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderBottom: 'none', borderLeft: 'none' }"
          />
        </span>
      </button>
    </template>

    <div class="flex-1" />

    <!-- Won / Lost pills -->
    <div class="flex items-center gap-1.5 px-3 border-l border-white/10">
      <button
        v-for="status in terminalStatuses"
        :key="status.name"
        class="rounded-full px-3 py-1 text-xs font-medium transition-all cursor-pointer border"
        :class="isActive(status) ? 'text-white border-transparent' : 'text-gray-400 border-white/20 hover:text-white hover:border-white/40'"
        :style="isActive(status) ? { backgroundColor: status.color } : {}"
        @click="$emit('change', status.name)"
      >
        {{ __(status.name) }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  statuses: { type: Array, default: () => [] },
  currentStatus: { type: String, default: '' },
})

defineEmits(['change'])

const mainStatuses = computed(() =>
  props.statuses.filter((s) => s.type !== 'Lost' && s.type !== 'Won')
)

const terminalStatuses = computed(() =>
  props.statuses.filter((s) => s.type === 'Lost' || s.type === 'Won')
)

function isActive(status) {
  return props.currentStatus === status.name
}
</script>
