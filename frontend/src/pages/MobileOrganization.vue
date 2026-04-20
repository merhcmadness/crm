<template>
  <LayoutHeader v-if="organization.doc">
    <header
      class="relative flex h-10.5 items-center justify-between gap-2 py-2.5 pl-2"
    >
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </header>
  </LayoutHeader>
  <div v-if="organization.doc" class="flex flex-col h-full overflow-hidden">
    <FileUploader
      :validateFile="validateIsImageFile"
      @success="changeOrganizationImage"
    >
      <template #default="{ openFileSelector, error }">
        <div class="flex flex-col items-start justify-start gap-4 p-4">
          <div class="flex gap-4 items-center">
            <div class="group relative h-14.5 w-14.5">
              <Avatar
                size="3xl"
                class="h-14.5 w-14.5"
                :label="organization.doc.organization_name"
                :image="organization.doc.organization_logo"
              />
              <component
                :is="organization.doc.organization_logo ? Dropdown : 'div'"
                v-bind="
                  organization.doc.organization_logo
                    ? {
                        options: [
                          {
                            icon: 'upload',
                            label: organization.doc.organization_logo
                              ? __('Change Image')
                              : __('Upload Image'),
                            onClick: openFileSelector,
                          },
                          {
                            icon: 'trash-2',
                            label: __('Remove Image'),
                            onClick: () => changeOrganizationImage(''),
                          },
                        ],
                      }
                    : { onClick: openFileSelector }
                "
                class="!absolute bottom-0 left-0 right-0"
              >
                <div
                  class="z-1 absolute bottom-0 left-0 right-0 flex h-14 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-5 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                  style="
                    -webkit-clip-path: inset(22px 0 0 0);
                    clip-path: inset(22px 0 0 0);
                  "
                >
                  <CameraIcon class="h-6 w-6 cursor-pointer text-white" />
                </div>
              </component>
            </div>
            <div class="flex flex-col gap-2 truncate">
              <div class="truncate text-lg font-medium text-ink-gray-9">
                {{ organization.doc.name }}
              </div>
              <div class="flex items-center gap-1.5">
                <Button @click="openWebsite">
                  <FeatherIcon name="link" class="h-4 w-4" />
                </Button>
                <Button
                  v-if="canDelete"
                  :label="__('Delete')"
                  theme="red"
                  size="sm"
                  iconLeft="trash-2"
                  @click="deleteOrganization"
                />
              </div>
              <ErrorMessage :message="__(error)" />
            </div>
          </div>
        </div>
      </template>
    </FileUploader>
    <Tabs
      v-model="tabIndex"
      as="div"
      :tabs="tabs"
      class="flex flex-1 overflow-auto flex-col [&_[role='tablist']]:gap-7.5 [&_[role='tablist']]:px-4 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
    >
      <template #tab-item="{ tab, selected }">
        <button
          v-if="tab.name !== 'Details'"
          class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-ink-gray-5 duration-300 ease-in-out hover:text-ink-gray-9"
          :class="{ 'text-ink-gray-9': selected }"
        >
          <component :is="tab.icon" v-if="tab.icon" class="h-5" />
          {{ __(tab.label) }}
          <Badge
            class="group-hover:bg-surface-gray-7"
            :class="[selected ? 'bg-surface-gray-7' : 'bg-gray-600']"
            variant="solid"
            theme="gray"
            size="sm"
          >
            {{ tab.count }}
          </Badge>
        </button>
      </template>
      <template #tab-panel="{ tab }">
        <div v-if="tab.name == 'Details'">
          <div
            v-if="sections.data"
            class="flex flex-1 flex-col justify-between overflow-hidden"
          >
            <SidePanelLayout
              :sections="sections.data"
              doctype="CRM Organization"
              :docname="organization.doc.name"
              @reload="sections.reload"
            />
          </div>
        </div>
        <DealsListView
          v-if="tab.label === 'Deals' && rows.length"
          class="mt-4"
          :rows="rows"
          :columns="columns"
          :options="{ selectable: false, showTooltip: false }"
        />
        <ContactsListView
          v-if="tab.label === 'Contacts' && rows.length"
          class="mt-4"
          :rows="rows"
          :columns="columns"
          :options="{ selectable: false, showTooltip: false }"
        />
        <div
          v-if="tab.label === 'Raven'"
          class="flex flex-1 flex-col gap-4 overflow-auto px-4 py-4"
        >
          <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-4">
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="text-base font-medium text-ink-gray-9">
                  {{ __('Raven Channel') }}
                </div>
                <p class="mt-1 text-sm text-ink-gray-6">
                  {{ __('Create a public Raven channel for this organization and link it directly to the CRM record.') }}
                </p>
              </div>
              <Badge
                variant="solid"
                theme="gray"
                size="sm"
                :class="isRavenLinked ? 'bg-surface-green-2 text-ink-green-3' : 'bg-surface-gray-3 text-ink-gray-6'"
              >
                {{ isRavenLinked ? __('Linked') : __('Not Linked') }}
              </Badge>
            </div>

            <div
              v-if="ravenChannel"
              class="mt-4 grid gap-3 rounded-lg bg-surface-gray-2 p-4 text-sm text-ink-gray-7"
            >
              <div>
                <span class="font-medium text-ink-gray-9">{{ __('Channel') }}:</span>
                {{ ravenChannel.channel_name }}
              </div>
              <div>
                <span class="font-medium text-ink-gray-9">{{ __('Type') }}:</span>
                {{ ravenChannel.type }}
              </div>
              <div>
                <span class="font-medium text-ink-gray-9">{{ __('Workspace') }}:</span>
                {{ ravenChannel.workspace }}
              </div>
            </div>

            <div class="mt-4 flex flex-wrap gap-2">
              <Button
                v-if="!ravenChannel"
                :label="isCreatingRavenChannel ? __('Creating...') : __('Create Public Channel')"
                icon-left="plus"
                variant="solid"
                :loading="isCreatingRavenChannel"
                @click="createRavenChannel"
              />
              <Button
                :label="__('Open Raven')"
                icon-left="external-link"
                :disabled="!ravenChannel && isCreatingRavenChannel"
                @click="openRavenChannel"
              />
            </div>
          </div>
        </div>
        <div
          v-if="!rows.length && tab.name !== 'Details' && tab.label !== 'Raven'"
          class="grid flex-1 place-items-center text-xl font-medium text-ink-gray-4"
        >
          <div class="flex flex-col items-center justify-center space-y-3">
            <component :is="tab.icon" class="!h-10 !w-10" />
            <div>{{ __('No {0} Found', [__(tab.label)]) }}</div>
          </div>
        </div>
      </template>
    </Tabs>
  </div>
</template>

<script setup>
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import Icon from '@/components/Icon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import { showAddressModal, addressProps } from '@/composables/modals'
import { useDocument } from '@/data/document'
import { getSettings } from '@/stores/settings'
import { getMeta } from '@/stores/meta'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { getView } from '@/utils/view'
import {
  formatDate,
  timeAgo,
  validateIsImageFile,
  openWebsite as openExternalWebsite,
} from '@/utils'
import {
  Breadcrumbs,
  Avatar,
  FileUploader,
  Dropdown,
  Tabs,
  call,
  createListResource,
  usePageMeta,
  createResource,
  toast,
} from 'frappe-ui'
import { h, computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  organizationId: { type: String, required: true },
})

const { brand } = getSettings()
const { getUser } = usersStore()
const { $dialog } = globalStore()
const { getDealStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Organization')

const route = useRoute()
const router = useRouter()

const {
  document: organization,
  permissions,
  triggerOnRender,
} = useDocument('CRM Organization', props.organizationId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

onMounted(async () => {
  if (organization.doc) await triggerOnRender()
})

const breadcrumbs = computed(() => {
  let items = [{ label: __('Organizations'), route: { name: 'Organizations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(
      route.query.view,
      route.query.viewType,
      'CRM Organization',
    )
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Organizations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: {
      name: 'Organization',
      params: { organizationId: props.organizationId },
    },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return organization.doc?.[t] || props.organizationId
})

usePageMeta(() => {
  return {
    title: title.value,
    icon: brand.favicon,
  }
})

async function changeOrganizationImage(file) {
  await call('frappe.client.set_value', {
    doctype: 'CRM Organization',
    name: props.organizationId,
    fieldname: 'organization_logo',
    value: file?.file_url || '',
  })
  organization.reload()
}

async function deleteOrganization() {
  $dialog({
    title: __('Delete Organization'),
    message: __('Are you sure you want to delete this organization?'),
    actions: [
      {
        label: __('Delete'),
        theme: 'red',
        variant: 'solid',
        async onClick(close) {
          await call('frappe.client.delete', {
            doctype: 'CRM Organization',
            name: props.organizationId,
          })
          close()
          router.push({ name: 'Organizations' })
        },
      },
    ],
  })
}

function openWebsite() {
  if (!organization.doc.website) {
    toast.error(__('No Website Found'))
    return
  }

  openExternalWebsite(organization.doc.website)
}

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Organization'],
  params: { doctype: 'CRM Organization' },
  auto: true,
  transform: (data) => getParsedSections(data),
})

function getParsedSections(_sections) {
  return _sections.map((section) => {
    section.columns = section.columns.map((column) => {
      column.fields = column.fields.map((field) => {
        if (field.fieldname === 'address') {
          return {
            ...field,
            create: (value, close) => {
              openAddressModal()
              close()
            },
            edit: (address) => openAddressModal(address),
          }
        } else {
          return field
        }
      })
      return column
    })
    return section
  })
}

const tabIndex = ref(0)
const isCreatingRavenChannel = ref(false)
const tabs = [
  {
    name: 'Details',
    label: __('Details'),
    icon: DetailsIcon,
  },
  {
    name: 'Deals',
    label: __('Deals'),
    icon: h(DealsIcon, { class: 'h-4 w-4' }),
    count: computed(() => deals.data?.length),
  },
  {
    name: 'Contacts',
    label: __('Contacts'),
    icon: h(ContactsIcon, { class: 'h-4 w-4' }),
    count: computed(() => contacts.data?.length),
  },
  {
    name: 'Raven',
    label: __('Raven'),
    icon: h(CommentIcon, { class: 'h-4 w-4' }),
    count: computed(() => (isRavenLinked.value ? 1 : 0)),
  },
]

const activeTab = computed(() => tabs[tabIndex.value]?.name)
const isRavenLinked = computed(() => {
  return Boolean(ravenChannel.value?.name)
})

const ravenChannelResource = createResource({
  url: 'crm.crm.api.raven.get_linked_raven_channel',
  params: { organization: props.organizationId },
  auto: true,
})

const ravenChannel = computed(() => ravenChannelResource.data?.channel || null)

const deals = createListResource({
  type: 'list',
  doctype: 'CRM Deal',
  cache: ['deals', props.organizationId],
  fields: [
    'name',
    'organization',
    'currency',
    'deal_value',
    'status',
    'email',
    'mobile_no',
    'deal_owner',
    'modified',
  ],
  filters: {
    organization: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const contacts = createListResource({
  type: 'list',
  doctype: 'Contact',
  cache: ['contacts', props.organizationId],
  fields: [
    'name',
    'full_name',
    'image',
    'email_id',
    'mobile_no',
    'company_name',
    'modified',
  ],
  filters: {
    company_name: props.organizationId,
  },
  orderBy: 'modified desc',
  pageLength: 20,
  auto: true,
})

const rows = computed(() => {
  let list = activeTab.value === 'Deals' ? deals : contacts

  if (!['Deals', 'Contacts'].includes(activeTab.value) || !list.data) return []

  return list.data.map((row) => {
    return activeTab.value === 'Deals'
      ? getDealRowObject(row)
      : getContactRowObject(row)
  })
})

const { getFormattedCurrency } = getMeta('CRM Deal')

const columns = computed(() => {
  return activeTab.value === 'Deals' ? dealColumns : contactColumns
})

async function createRavenChannel() {
  isCreatingRavenChannel.value = true
  try {
    let response = await call('crm.crm.api.raven.create_public_raven_channel', {
      organization: props.organizationId,
    })
    await Promise.all([organization.reload(), ravenChannelResource.reload()])
    toast.success(
      response?.created
        ? __('Public Raven channel created')
        : __('Raven channel already linked'),
    )
  } finally {
    isCreatingRavenChannel.value = false
  }
}

function openRavenChannel() {
  const route = ravenChannel.value?.route || '/raven'
  window.open(`${window.location.origin}${route}`, '_blank')
}

function getDealRowObject(deal) {
  return {
    name: deal.name,
    organization: {
      label: deal.organization,
      logo: organization.doc?.organization_logo,
    },
    deal_value: getFormattedCurrency('deal_value', deal),
    status: {
      label: deal.status,
      color: getDealStatus(deal.status)?.color,
    },
    email: deal.email,
    mobile_no: deal.mobile_no,
    deal_owner: {
      label: deal.deal_owner && getUser(deal.deal_owner).full_name,
      ...(deal.deal_owner && getUser(deal.deal_owner)),
    },
    modified: {
      label: formatDate(deal.modified),
      timeAgo: __(timeAgo(deal.modified)),
    },
  }
}

function getContactRowObject(contact) {
  return {
    name: contact.name,
    full_name: {
      label: contact.full_name,
      image_label: contact.full_name,
      image: contact.image,
    },
    email: contact.email_id,
    mobile_no: contact.mobile_no,
    company_name: {
      label: contact.company_name,
      logo: organization.doc?.organization_logo,
    },
    modified: {
      label: formatDate(contact.modified),
      timeAgo: __(timeAgo(contact.modified)),
    },
  }
}

const dealColumns = [
  {
    label: __('Organization'),
    key: 'organization',
    width: '11rem',
  },
  {
    label: __('Amount'),
    key: 'deal_value',
    align: 'right',
    width: '9rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '10rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Mobile No.'),
    key: 'mobile_no',
    width: '11rem',
  },
  {
    label: __('Deal Owner'),
    key: 'deal_owner',
    width: '10rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '8rem',
  },
]

const contactColumns = [
  {
    label: __('Name'),
    key: 'full_name',
    width: '17rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '12rem',
  },
  {
    label: __('Phone'),
    key: 'mobile_no',
    width: '12rem',
  },
  {
    label: __('Organization'),
    key: 'company_name',
    width: '12rem',
  },
  {
    label: __('Last Modified'),
    key: 'modified',
    width: '8rem',
  },
]

function openAddressModal(_address) {
  showAddressModal.value = true
  addressProps.value = {
    doctype: 'Address',
    address: _address,
  }
}
</script>
