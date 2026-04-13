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
              <Badge :label="q.status" size="sm" :theme="statusTheme(q.status)" variant="subtle" />
              <span class="text-xs text-ink-gray-5">{{ formatCurrency(q.grand_total, q.currency) }}</span>
            </div>
          </div>
        </div>

        <div v-if="docs.sales_orders?.length" class="flex flex-col gap-1">
          <div class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide mb-1 mt-2">{{ __('Sales Orders') }}</div>
          <div
            v-for="o in docs.sales_orders"
            :key="o.name"
            class="flex items-center justify-between rounded-md px-3 py-2 text-sm bg-surface-gray-2 hover:bg-surface-gray-3 cursor-pointer"
            @click="openDoc('sales-order', o.name)"
          >
            <span class="font-medium text-ink-gray-8">{{ o.name }}</span>
            <div class="flex items-center gap-2">
              <Badge :label="o.status" size="sm" :theme="statusTheme(o.status)" variant="subtle" />
              <span class="text-xs text-ink-gray-5">{{ formatCurrency(o.grand_total, o.currency) }}</span>
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

        <div v-if="docs.projects?.length" class="flex flex-col gap-1">
          <div class="text-xs font-medium text-ink-gray-5 uppercase tracking-wide mb-1 mt-2">{{ __('Projects') }}</div>
          <div
            v-for="p in docs.projects"
            :key="p.name"
            class="flex items-center justify-between rounded-md px-3 py-2 text-sm bg-surface-gray-2 hover:bg-surface-gray-3 cursor-pointer"
            @click="openDoc('project', p.name)"
          >
            <span class="font-medium text-ink-gray-8">{{ p.name }}</span>
            <div class="flex items-center gap-2">
              <Badge :label="p.status" size="sm" variant="subtle" />
              <span class="text-xs text-ink-gray-5">{{ p.percent_complete?.toFixed(0) }}%</span>
            </div>
          </div>
        </div>

        <div
          v-if="!docs.quotations?.length && !docs.sales_orders?.length && !docs.invoices?.length && !docs.projects?.length"
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
          <Button
            v-if="dealStatus === 'Won'"
            class="w-full"
            variant="subtle"
            :label="__('Create DP Invoice')"
            :loading="creatingDPInvoice"
            @click="showDPDialog = true"
          />
          <Button
            v-if="dealStatus === 'Won' && !docs.projects?.length"
            class="w-full"
            variant="subtle"
            :label="__('Create Project')"
            :loading="creatingProject"
            @click="createProject"
          />
        </div>
      </template>
    </div>

    <!-- DP Invoice Dialog -->
    <Dialog v-model="showDPDialog" :options="{ title: __('Create Down Payment Invoice') }">
      <template #body-content>
        <div class="flex flex-col gap-3">
          <div>
            <label class="text-sm text-ink-gray-6 mb-1 block">{{ __('Customer PO Number') }}</label>
            <input
              v-model="dpPoNo"
              type="text"
              class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm"
              :placeholder="__('e.g. PO-2024-001')"
            />
          </div>
          <div>
            <label class="text-sm text-ink-gray-6 mb-1 block">{{ __('Down Payment %') }}</label>
            <input
              v-model="dpPercent"
              type="number"
              min="1"
              max="100"
              class="w-full border border-outline-gray-2 rounded px-3 py-2 text-sm"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="solid" :label="__('Create Invoice')" :loading="creatingDPInvoice" @click="createDPInvoice" />
        <Button variant="subtle" :label="__('Cancel')" @click="showDPDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import { createResource, Badge, Button, Dialog, call, toast } from 'frappe-ui'
import { ref, computed } from 'vue'

const props = defineProps({
  dealId: { type: String, required: true },
  dealStatus: { type: String, default: '' },
})

const opened = ref(true)
const creatingProject = ref(false)
const creatingQuotation = ref(false)
const creatingDPInvoice = ref(false)
const showDPDialog = ref(false)
const dpPercent = ref(50)
const dpPoNo = ref('')

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

async function createDPInvoice() {
  creatingDPInvoice.value = true
  try {
    const result = await call('merch_madness_customizations.api.crm.create_dp_invoice', {
      deal: props.dealId,
      dp_percent: dpPercent.value,
      po_no: dpPoNo.value,
    })
    toast.success(__('DP Invoice created: ') + result.name)
    showDPDialog.value = false
    linkedDocs.reload()
    openDoc('sales-invoice', result.name)
  } catch (e) {
    toast.error(e.messages?.[0] || __('Failed to create DP invoice'))
  } finally {
    creatingDPInvoice.value = false
  }
}

async function createProject() {
  creatingProject.value = true
  try {
    const name = await call('crm.api.erpnext_links.create_project_from_deal', { deal: props.dealId })
    toast.success(__('Project created: ') + name)
    linkedDocs.reload()
  } catch (e) {
    toast.error(e.messages?.[0] || __('Failed to create project'))
  } finally {
    creatingProject.value = false
  }
}
</script>
