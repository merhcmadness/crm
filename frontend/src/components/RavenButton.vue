<template>
  <div>
    <!-- Floating Raven button -->
    <button
      class="fixed bottom-6 right-6 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-ink-gray-9 shadow-xl hover:bg-ink-gray-8 transition-colors"
      :title="__('Open Raven')"
      @click="toggleRaven"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" viewBox="0 0 24 24" fill="currentColor">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
      </svg>
    </button>

    <!-- Raven iframe panel -->
    <div
      v-if="ravenOpen"
      class="fixed bottom-20 right-6 z-50 flex flex-col rounded-xl shadow-2xl overflow-hidden"
      style="width: 420px; height: 600px;"
    >
      <div class="flex items-center justify-between bg-ink-gray-9 px-4 py-2">
        <span class="text-sm font-medium text-white">Raven</span>
        <div class="flex items-center gap-2">
          <button
            class="text-white opacity-70 hover:opacity-100 text-xs"
            @click="openFullscreen"
          >
            ↗
          </button>
          <button
            class="text-white opacity-70 hover:opacity-100"
            @click="ravenOpen = false"
          >
            ✕
          </button>
        </div>
      </div>
      <iframe
        ref="ravenIframe"
        :src="ravenUrl"
        class="flex-1 w-full border-0 bg-white"
        allow="microphone"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const ravenOpen = ref(false)
const ravenIframe = ref(null)

const ravenUrl = computed(() => `${window.location.origin}/raven`)

function toggleRaven() {
  ravenOpen.value = !ravenOpen.value
}

function openFullscreen() {
  window.open(ravenUrl.value, '_blank')
}
</script>
