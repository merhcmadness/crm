<template>
  <div class="flex items-stretch overflow-x-auto border-b bg-surface-gray-2 select-none" style="min-height: 44px;">
    <!-- Main statuses as chevrons -->
    <template v-for="(status, i) in mainStatuses" :key="status.name">
      <button
        class="relative flex items-center justify-center px-5 py-2 text-xs font-medium transition-colors cursor-pointer"
        :class="[
          i === 0 ? 'pl-4' : 'pl-7',
          isActive(status) ? 'text-ink-gray-9' : 'text-ink-gray-5 hover:text-ink-gray-8',
          isActive(status) ? 'bg-surface-white' : 'hover:bg-surface-gray-3',
        ]"
        :style="isActive(status) ? { boxShadow: `inset 0 -2px 0 ${status.color}` } : {}"
        @click="$emit('change', status.name)"
      >
        <!-- Left arrow notch (all except first) -->
        <span
          v-if="i > 0"
          class="absolute left-0 top-0 h-full w-5 overflow-hidden"
          style="pointer-events: none;"
        >
          <span
            class="absolute left-0 top-1/2 -translate-y-1/2 border-y-[22px] border-l-[10px] border-y-transparent"
            :class="isActive(status) ? 'border-l-surface-white' : 'border-l-surface-gray-2 group-hover:border-l-surface-gray-3'"
            style="border-left-color: inherit;"
          />
        </span>

        <!-- Label -->
        <span class="relative z-10 whitespace-nowrap">{{ __(status.name) }}</span>

        <!-- Right arrow point -->
        <span
          v-if="i < mainStatuses.length - 1"
          class="absolute right-0 top-0 z-10 h-full w-4 overflow-hidden"
          style="pointer-events: none;"
        >
          <span
            class="absolute -right-2 top-1/2 h-6 w-6 -translate-y-1/2 rotate-45 border-r border-t"
            :class="isActive(status) ? 'bg-surface-white border-outline-gray-2' : 'bg-surface-gray-2 border-outline-gray-2'"
          />
        </span>
      </button>
    </template>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Terminal statuses (Won / Lost) on the right -->
    <div class="flex items-center gap-1.5 px-3 border-l">
      <button
        v-for="status in terminalStatuses"
        :key="status.name"
        class="rounded-full px-3 py-1 text-xs font-medium transition-colors cursor-pointer"
        :class="isActive(status) ? 'text-white' : 'text-ink-gray-5 hover:text-ink-gray-9 bg-surface-gray-3 hover:bg-surface-gray-4'"
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
