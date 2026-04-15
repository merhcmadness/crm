<template>
  <div
    v-if="metrics"
    class="flex items-stretch border-b border-outline-gray-modals bg-surface-white overflow-x-auto shrink-0"
  >
    <div
      v-for="metric in metricsList"
      :key="metric.label"
      class="flex flex-col justify-center gap-1.5 px-8 py-4 border-r border-outline-gray-modals last:border-r-0 min-w-[160px]"
    >
      <div class="text-[11px] font-semibold uppercase tracking-widest text-ink-gray-5 whitespace-nowrap">
        {{ metric.label }}
      </div>
      <div class="text-2xl font-bold text-cyan-700 whitespace-nowrap leading-tight">
        {{ metric.value }}
      </div>
      <div v-if="metric.sub" class="text-xs text-ink-gray-5 whitespace-nowrap">
        {{ metric.sub }}
      </div>
    </div>
  </div>
  <div v-else-if="metricsResource.loading" class="flex items-center px-6 py-4 border-b border-outline-gray-modals bg-surface-white shrink-0">
    <div class="text-xs text-ink-gray-5">Loading metrics…</div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { computed, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({}),
  },
})

const metricsResource = createResource({
  url: 'merch_madness_customizations.api.deal_metrics.get_deal_metrics',
  params: { filters: JSON.stringify(props.filters) },
  auto: true,
})

watch(
  () => props.filters,
  (val) => {
    metricsResource.params = { filters: JSON.stringify(val || {}) }
    metricsResource.reload()
  },
  { deep: true },
)

const metrics = computed(() => metricsResource.data)

function fmt(amount) {
  if (amount === undefined || amount === null) return '—'
  if (amount >= 1_000_000_000) {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(amount)
  }
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(amount)
}

const metricsList = computed(() => {
  const d = metrics.value
  if (!d) return []
  return [
    {
      label: 'Total Deal Amount',
      value: fmt(d.total_amount),
      sub: `Avg per deal ${fmt(d.avg_deal_value)}`,
    },
    {
      label: 'Weighted Amount',
      value: fmt(d.weighted_amount),
      sub: 'Value × probability',
    },
    {
      label: 'Open Amount',
      value: fmt(d.open_amount),
    },
    {
      label: 'Closed Won',
      value: fmt(d.won_amount),
    },
    {
      label: 'Closed Lost',
      value: fmt(d.lost_amount),
    },
    {
      label: 'Deal Count',
      value: d.deal_count.toLocaleString('id-ID'),
    },
  ]
})
</script>
