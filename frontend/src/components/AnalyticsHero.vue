<script setup lang="ts">
import { computed } from 'vue'
import { Button, CircularProgressBar } from 'frappe-ui'
import {
  LucideAlertCircle, LucideCheckCircle, LucideListChecks, LucideRefreshCw,
} from 'lucide-vue-next'
import type { OverallStats } from '@/types'

const props = defineProps<{
  studentName: string
  overall: OverallStats
  regrading: boolean
}>()
defineEmits<{ (e: 'regrade'): void; (e: 'jump-fix'): void }>()

const pct = computed(() =>
  props.overall.chkTotal ? Math.round((props.overall.chkPassed / props.overall.chkTotal) * 100) : 0,
)
const toFix = computed(() => props.overall.chkTotal - props.overall.chkPassed)
const statusLine = computed(() => {
  const p = pct.value
  if (p === 100) return "All checks pass — you're ready to submit."
  if (p >= 70) return 'Almost there — just a few items left to fix.'
  if (p >= 30) return 'Good start. Keep working through the red items.'
  return "Let's get started — work through the sections below."
})
</script>

<template>
  <section class="mb-4 rounded-2xl border border-outline-gray-2 bg-surface-white p-6">
    <div class="flex items-start justify-between gap-5 border-b border-outline-gray-1 pb-5">
      <div>
        <span class="text-xs font-bold uppercase tracking-wider text-ink-green-3">
          Your course site checker
        </span>
        <h1 class="mt-1.5 text-2xl font-bold tracking-tight text-ink-gray-9">
          Hi {{ studentName }} — here's how your ERPNext site is doing
        </h1>
        <p class="mt-2 max-w-2xl text-base text-ink-gray-6">
          We automatically check your practice site against each assignment.
          <b class="font-semibold text-ink-green-3">Green means done.</b>
          <b class="font-semibold text-ink-red-3">Red means it still needs work.</b>
          Fix the red items below, then press Re-check.
        </p>
      </div>
      <Button variant="solid" theme="gray" :loading="regrading" @click="$emit('regrade')">
        <template #prefix><LucideRefreshCw class="size-4" /></template>
        {{ regrading ? 'Checking your site…' : 'Re-check site' }}
      </Button>
    </div>

    <div class="grid grid-cols-1 items-center gap-6 pt-5 md:grid-cols-[minmax(280px,1fr)_minmax(0,1.4fr)]">
      <div class="flex items-center gap-4">
        <CircularProgressBar :step="overall.chkPassed" :total-steps="overall.chkTotal || 1"
          :show-percentage="true" theme="green" size="lg" />
        <div class="flex flex-col gap-1">
          <strong class="text-base font-semibold text-ink-gray-9">{{ statusLine }}</strong>
          <span class="text-sm text-ink-gray-5">
            {{ overall.chkPassed }} of {{ overall.chkTotal }} checks passing
          </span>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2.5">
        <div class="flex min-h-[92px] flex-col justify-end gap-0.5 rounded-xl border
                    border-outline-gray-2 p-3.5">
          <LucideCheckCircle class="mb-auto size-5 text-ink-green-3" />
          <span class="text-2xl font-bold text-ink-green-3">{{ overall.chkPassed }}</span>
          <span class="text-xs text-ink-gray-5">Checks passed</span>
        </div>
        <button
          class="flex min-h-[92px] flex-col justify-end gap-0.5 rounded-xl border
                 border-outline-gray-2 p-3.5 text-left enabled:hover:border-outline-red-1
                 disabled:cursor-default"
          :disabled="toFix === 0" @click="$emit('jump-fix')"
        >
          <LucideAlertCircle class="mb-auto size-5 text-ink-red-3" />
          <span class="text-2xl font-bold text-ink-red-3">{{ toFix }}</span>
          <span class="text-xs text-ink-gray-5">Still to fix</span>
        </button>
        <div class="flex min-h-[92px] flex-col justify-end gap-0.5 rounded-xl border
                    border-outline-gray-2 p-3.5">
          <LucideListChecks class="mb-auto size-5 text-ink-gray-6" />
          <span class="text-2xl font-bold text-ink-gray-9">
            {{ overall.secPassed }}/{{ overall.secTotal }}
          </span>
          <span class="text-xs text-ink-gray-5">Sections done</span>
        </div>
      </div>
    </div>
  </section>
</template>
