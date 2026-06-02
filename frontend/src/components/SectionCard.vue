<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Badge } from 'frappe-ui'
import { LucideChevronDown, LucideFileText, LucideListChecks } from 'lucide-vue-next'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import CheckRow from './CheckRow.vue'
import type { SectionState } from '@/types'

const props = defineProps<{ state: SectionState; index: number; defaultOpen: boolean }>()
const emit = defineEmits<{ (e: 'mounted', name: string, el: HTMLElement): void }>()

const open = ref(props.defaultOpen)
const root = ref<HTMLElement | null>(null)
onMounted(() => root.value && emit('mounted', props.state.section.name, root.value))

const theme = computed(() =>
  props.state.status === 'passed' ? 'green' : props.state.status === 'partial' ? 'orange' : 'red')
const label = computed(() =>
  props.state.status === 'passed' ? 'Passed'
  : props.state.status === 'partial' ? 'In progress' : 'Not started')
const html = computed(() =>
  DOMPurify.sanitize(marked.parse(props.state.section.assignment_details ?? '') as string))
const borderClass = computed(() =>
  props.state.status === 'passed' ? 'border-l-4 border-l-surface-green-3'
  : props.state.status === 'partial' ? 'border-l-4 border-l-surface-amber-3'
  : 'border-l-4 border-l-surface-red-3')
</script>

<template>
  <section ref="root" :id="`sec-${state.section.name}`"
    class="scroll-mt-24 overflow-hidden rounded-2xl border border-outline-gray-2 bg-surface-white"
    :class="borderClass">
    <button class="flex w-full items-center gap-3.5 px-6 py-5 text-left"
      :class="open ? 'border-b border-outline-gray-1' : ''" @click="open = !open">
      <span class="shrink-0 text-sm font-bold tabular-nums text-ink-gray-3">
        {{ String(index + 1).padStart(2, '0') }}
      </span>
      <div class="min-w-0 flex-1">
        <h3 class="text-lg font-semibold tracking-tight text-ink-gray-9">{{ state.section.section }}</h3>
        <p v-if="state.section.blurb" class="mt-0.5 text-sm text-ink-gray-5">{{ state.section.blurb }}</p>
      </div>
      <Badge :theme="theme" :label="`${label} · ${state.passed}/${state.total}`" />
      <LucideChevronDown class="size-5 shrink-0 text-ink-gray-4 transition" :class="open ? 'rotate-180' : ''" />
    </button>

    <div v-if="open" class="grid grid-cols-1 md:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]">
      <div class="border-b border-outline-gray-1 bg-surface-gray-1 p-6 md:border-b-0 md:border-r">
        <div class="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-4">
          <LucideFileText class="size-3.5" /><span>What to do</span>
        </div>
        <!-- assignment_details is instructor-authored; sanitized above per security.md §3 -->
        <div class="prose prose-sm max-w-none text-ink-gray-6" v-html="html" />
      </div>
      <div class="p-6">
        <div class="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-4">
          <LucideListChecks class="size-3.5" /><span>Checks</span>
          <span class="ml-auto text-xs font-semibold normal-case tabular-nums text-ink-gray-5">
            {{ state.passed }}/{{ state.total }} passing
          </span>
        </div>
        <div class="flex flex-col gap-4">
          <div v-for="g in state.groups" :key="g.title">
            <div v-if="g.title" class="mb-1 flex items-baseline justify-between border-b
                 border-outline-gray-1 px-1 pb-2 text-sm font-semibold text-ink-gray-7">
              <span>{{ g.title }}</span>
              <span class="text-xs font-semibold tabular-nums text-ink-gray-4">
                {{ g.checks.filter((c) => c.passed).length }}/{{ g.checks.length }}
              </span>
            </div>
            <div class="flex flex-col gap-0.5">
              <CheckRow v-for="(c, i) in g.checks" :key="i" :check="c" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
