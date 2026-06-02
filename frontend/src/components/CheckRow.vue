<script setup lang="ts">
import { ref } from 'vue'
import { LucideCheck, LucideChevronDown, LucideX } from 'lucide-vue-next'
import type { CheckResult } from '@/types'

const props = defineProps<{ check: CheckResult }>()
const open = ref(false)
</script>

<template>
  <div class="rounded-md" :class="!check.passed ? 'bg-surface-red-1' : ''">
    <button class="flex w-full items-center gap-3 px-2.5 py-2 text-left"
      :style="{ cursor: check.passed ? 'default' : 'pointer' }"
      @click="!check.passed && (open = !open)">
      <span class="grid size-5 shrink-0 place-items-center rounded-full"
        :class="check.passed ? 'bg-surface-green-2 text-ink-green-3' : 'bg-surface-red-2 text-ink-red-3'">
        <component :is="check.passed ? LucideCheck : LucideX" class="size-3" :stroke-width="3" />
      </span>
      <span class="flex-1 text-base text-ink-gray-7">{{ check.label }}</span>
      <LucideChevronDown v-if="!check.passed" class="size-4 shrink-0 text-ink-gray-4 transition"
        :class="open ? 'rotate-180' : ''" />
    </button>
    <div v-if="!check.passed && open"
      class="mb-2 ml-[42px] mr-2.5 flex flex-col gap-1.5 rounded-md border border-outline-gray-2
             bg-surface-white p-3">
      <div class="grid grid-cols-[64px_1fr] gap-2.5 text-xs">
        <span class="font-semibold uppercase text-ink-gray-4">Expected</span>
        <span class="font-mono text-ink-gray-7">{{ check.expected }}</span>
      </div>
      <div class="grid grid-cols-[64px_1fr] gap-2.5 text-xs">
        <span class="font-semibold uppercase text-ink-gray-4">Actual</span>
        <span class="font-mono text-ink-red-3">{{ check.actual }}</span>
      </div>
    </div>
  </div>
</template>
