<template>
  <div class="flex flex-col">
    <div
      class="flex items-center justify-between px-5 py-3 border-b border-outline-gray-modals cursor-pointer select-none"
      @click="opened = !opened"
    >
      <span class="text-sm font-medium text-ink-gray-7">{{ __('ERPNext Documents') }}</span>
      <Button variant="ghost" class="h-6 w-6 p-0" :icon="opened ? 'chevron-down' : 'chevron-right'" />
    </div>

    <div v-if="opened" class="flex flex-col gap-2 px-5 py-3">
      <div v-if="linkedDocs.loading" class="flex justify-center py-3">
        <LoadingIndicator class="h-4 w-4" />
      </div>

      <template v-else>
        <div v-if="docs.quotations?.length" class="flex flex-col gap-1">
          <div class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide mb-1">{{ __('Quotations') }}</div>
          <div
            v-for="q in docs.quotations"
            :key="q.name"
            class="flex items-center justify-between rounded-md px-3 py-2 text-sm bg-surface-gray-2 hover:bg-surface-gray-3 cursor-pointer"
            @click="openDoc('quotation', q.name)"
          >
            <span class="font-medium text-ink-gray-8">{{ q.name }}</span>
            <div class="flex items-center gap-2">
              <Badge :label="quoteStatusLabel(q)" size="sm" :theme="quoteStatusTheme(q)" variant="subtle" />
              <span class="text-xs text-ink-gray-5">{{ formatCurrency(q.grand_total, q.currency) }}</span>
            </div>
          </div>
        </div>

        <div v-if="docs.invoices?.length" class="flex flex-col gap-1">
          <div class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide mb-1 mt-2">{{ __('Invoices') }}</div>
          <div
            v-for="inv in docs.invoices"
            :key="inv.name"
            class="flex items-center justify-between rounded-md px-3 py-2 text-sm bg-surface-gray-2 hover:bg-surface-gray-3 cursor-pointer"
            @click="openDoc('sales-invoice', inv.name)"
          >
            <span class="font-medium text-ink-gray-8">{{ inv.name }}</span>
            <div class="flex items-center gap-2">
              <Badge :label="inv.status" size="sm" :theme="statusTheme(inv.status)" variant="subtle" />
              <span class="text-xs text-ink-gray-5">{{ formatCurrency(inv.grand_total, inv.currency) }}</span>
            </div>
          </div>
        </div>

        <div v-if="docs.work_orders?.length" class="flex flex-col gap-1">
          <div class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide mb-1 mt-2">{{ __('Work Orders') }}</div>
          <div
            v-for="wo in docs.work_orders"
            :key="wo.name"
            class="flex items-center justify-between rounded-md px-3 py-2 text-sm bg-surface-gray-2 hover:bg-surface-gray-3 cursor-pointer"
            @click="openDoc('work-order', wo.name)"
          >
            <span class="font-medium text-ink-gray-8">{{ wo.production_item }}</span>
            <div class="flex items-center gap-2">
              <Badge :label="wo.status" size="sm" :theme="woStatusTheme(wo.status)" variant="subtle" />
              <span class="text-xs text-ink-gray-5">{{ wo.qty }} pcs</span>
            </div>
          </div>
        </div>

        <div
          v-if="!docs.quotations?.length && !docs.invoices?.length && !docs.work_orders?.length"
          class="flex items-center justify-center py-4 text-sm text-ink-gray-4"
        >
          {{ __('No linked documents') }}
        </div>

        <!-- Action buttons -->
        <div class="flex flex-col gap-2 mt-2">
          <Button
            class="w-full"
            variant="subtle"
            :label="__('New Quotation')"
            :loading="creatingQuotation"
            @click="createQuotation"
          />
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import { createResource, Badge, Button, call, toast } from 'frappe-ui'
import { ref, computed } from 'vue'

const props = defineProps({
  dealId: { type: String, required: true },
  dealStatus: { type: String, default: '' },
})

const opened = ref(true)
const creatingQuotation = ref(false)

const linkedDocs = createResource({
  url: 'crm.api.erpnext_links.get_linked_docs',
  params: { deal: props.dealId },
  auto: true,
})

const docs = computed(() => linkedDocs.data || {})

function openDoc(path, name) {
  window.open(`${window.location.origin}/app/${path}/${encodeURIComponent(name)}`, '_blank')
}

function statusTheme(status) {
  const map = {
    Draft: 'gray', Submitted: 'blue', Ordered: 'green', Paid: 'green',
    Unpaid: 'orange', Overdue: 'red', Cancelled: 'red', Completed: 'green', Open: 'blue',
  }
  return map[status] || 'gray'
}

function quoteStatusLabel(quote) {
  const signingStatus = quote.custom_docuseal_status
  const map = {
    'Draft Quote': __('Draft Quote'),
    'Quote Sent': __('Quote Sent'),
    Pending: __('Pending Signature'),
    'Pending Signature': __('Pending Signature'),
    'Awaiting Internal Signature': __('Awaiting Internal Signature'),
    Completed: __('Signed / Accepted'),
    'Signed / Accepted': __('Signed / Accepted'),
    Superseded: __('Superseded'),
  }
  return map[signingStatus] || quote.status
}

function quoteStatusTheme(quote) {
  const signingStatus = quote.custom_docuseal_status
  const map = {
    'Draft Quote': 'gray',
    'Quote Sent': 'blue',
    Pending: 'orange',
    'Pending Signature': 'orange',
    'Awaiting Internal Signature': 'blue',
    Completed: 'green',
    'Signed / Accepted': 'green',
    Superseded: 'gray',
  }
  return map[signingStatus] || statusTheme(quote.status)
}

function woStatusTheme(status) {
  const map = {
    Draft: 'gray', 'Not Started': 'gray', 'In Process': 'blue',
    Completed: 'green', Stopped: 'red', Cancelled: 'red',
  }
  return map[status] || 'gray'
}

function formatCurrency(amount, currency) {
  if (!amount) return ''
  return new Intl.NumberFormat('id-ID', {
    style: 'currency', currency: currency || 'IDR', maximumFractionDigits: 0,
  }).format(amount)
}

async function createQuotation() {
  creatingQuotation.value = true
  try {
    const name = await call('merch_madness_customizations.api.crm.create_quotation_from_deal', { deal: props.dealId })
    toast.success(__('Quotation created: ') + name)
    linkedDocs.reload()
    openDoc('quotation', name)
  } catch (e) {
    toast.error(e.messages?.[0] || __('Failed to create quotation'))
  } finally {
    creatingQuotation.value = false
  }
}
</script>
