<script setup lang="ts">
import { computed, ref } from 'vue'
import { LucideSearch } from 'lucide-vue-next'
import type { SectionState } from '@/types'

const props = defineProps<{ states: SectionState[]; activeName: string | null }>()
defineEmits<{ (e: 'jump', name: string): void }>()

const query = ref('')
const visible = computed(() =>
  props.states.filter((s) =>
    s.section.section.toLowerCase().includes(query.value.toLowerCase()),
  ),
)
const dotClass = (s: SectionState) =>
  s.status === 'passed' ? 'bg-surface-green-3'
  : s.status === 'partial' ? 'bg-surface-amber-3' : 'bg-surface-red-3'
</script>

<template>
  <nav class="sticky top-[60px] hidden h-[calc(100vh-60px)] flex-col border-r
              border-outline-gray-2 p-4 lg:flex">
    <div class="mb-3.5 flex h-9 items-center gap-2 rounded-md border border-outline-gray-2 px-2.5">
      <LucideSearch class="size-4 text-ink-gray-4" />
      <input v-model="query" placeholder="Filter sections"
        class="w-full bg-transparent text-sm text-ink-gray-9 outline-none" />
    </div>
    <div class="px-2 pb-2 text-[10.5px] font-bold uppercase tracking-wider text-ink-gray-4">
      Sections
    </div>
    <div class="-mx-1 flex-1 overflow-y-auto px-1">
      <div class="flex flex-col gap-0.5">
        <button v-for="s in visible" :key="s.section.name"
          class="flex items-center gap-2.5 rounded-md px-2.5 py-2 text-left text-base
                 text-ink-gray-6 hover:bg-surface-gray-2"
          :class="activeName === s.section.name ? 'bg-surface-gray-2 font-semibold text-ink-gray-9' : ''"
          @click="$emit('jump', s.section.name)"
        >
          <span class="size-2.5 shrink-0 rounded-full" :class="dotClass(s)" />
          <span class="flex-1 truncate">{{ s.section.section }}</span>
          <span class="text-xs font-semibold tabular-nums text-ink-gray-4">
            {{ s.passed }}/{{ s.total }}
          </span>
        </button>
      </div>
    </div>
  </nav>
</template>
