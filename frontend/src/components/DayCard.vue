<template>
	<AccordionCard
		:index="index"
		:title="`Day ${day.day}`"
		:open="defaultOpen"
		:status="dayState.status"
		:badge-label="dayState.badgeLabel"
	>
		<div class="space-y-4">
			<div class="grid gap-4 md:grid-cols-2">
				<section class="min-w-0">
					<div class="mb-2 flex h-8 items-center gap-2">
						<FileText class="size-3.5" />
						<span class="text-p-sm font-semibold uppercase tracking-widest">
							Assignment
						</span>
					</div>
					<div
						v-if="day.assignment_details"
						class="prose prose-sm max-w-none rounded-md border border-outline-gray-1 bg-surface-gray-1 p-3 text-ink-gray-8"
						v-html="renderedDetails"
					/>
					<p v-else class="text-p-sm text-ink-gray-6">No details provided.</p>
				</section>

				<section class="min-w-0">
					<div class="mb-2 flex h-8 items-center justify-between gap-2">
						<div class="flex items-center gap-2">
							<ListChecks class="size-3.5" />
							<span class="text-p-sm font-semibold uppercase tracking-widest">
								Checks
							</span>
						</div>
						<Button
							v-if="!dayState.passed"
							variant="solid"
							:loading="isGrading"
							:disabled="!connected"
							@click="$emit('grade', day.name)"
						>
							{{ dayState.best ? "Regrade" : "Submit" }}
						</Button>
					</div>
					<div v-if="isGrading" class="flex justify-center py-8">
						<LoadingIndicator class="size-6 text-ink-gray-5" />
					</div>
					<ul v-else-if="dayState.best?.results?.length">
						<CheckRow
							v-for="(r, idx) in dayState.best.results"
							:key="idx"
							:label="r.label"
							:state="r.passed ? 'pass' : 'fail'"
							:expected="r.expected"
							:actual="r.actual"
						/>
					</ul>
					<p v-else class="text-p-sm text-ink-gray-6">
						Not graded yet — submit to run the checks.
					</p>
				</section>
			</div>

			<details
				v-if="dayState.submissions.length > 1"
				class="group/attempts border-t border-outline-gray-1 pt-3"
			>
				<summary
					class="flex cursor-pointer items-center justify-between gap-2 list-none [&::-webkit-details-marker]:hidden"
				>
					<div class="flex items-center gap-2">
						<History class="size-3.5" />
						<span class="text-p-sm font-semibold uppercase tracking-widest">
							Past attempts
						</span>
						<Badge theme="gray">{{ dayState.submissions.length }}</Badge>
					</div>
					<ChevronRight
						class="size-3.5 text-ink-gray-6 transition-transform group-open/attempts:rotate-90"
					/>
				</summary>
				<ul class="mt-2 space-y-1">
					<li v-for="s in dayState.submissions" :key="s.name">
						<details class="group/attempt">
							<summary
								class="flex cursor-pointer list-none items-center justify-between gap-3 rounded-md p-2 hover:bg-surface-gray-2"
							>
								<div class="flex items-center gap-2">
									<ChevronRight
										class="size-3 text-ink-gray-5 transition-transform group-open/attempt:rotate-90"
									/>
									<span class="text-p-sm text-ink-gray-7">
										{{ formatTime(s.submission_time) }}
									</span>
								</div>
								<Badge :theme="s.status === 'Passed' ? 'green' : 'red'">
									{{ s.passed_checks }}/{{ s.total_checks }}
								</Badge>
							</summary>
							<ul v-if="failedResults(s).length" class="flex flex-col gap-3 ml-7 mt-2">
								<li
									v-for="(r, idx) in failedResults(s)"
									:key="idx"
									class="flex items-center gap-2"
								>
									<span
										class="flex size-4 shrink-0 items-center justify-center rounded-full bg-surface-red-2 text-ink-red-3"
									>
										<X class="size-3" />
									</span>
									<span class="text-p-sm text-ink-gray-8">{{ r.label }}</span>
								</li>
							</ul>
							<p v-else class="mt-1.5 ml-7 text-p-sm text-ink-gray-5">
								{{
									s.status === "Passed"
										? "All checks passed."
										: "No details available."
								}}
							</p>
						</details>
					</li>
				</ul>
			</details>
		</div>
	</AccordionCard>
</template>

<script setup lang="ts">
import DOMPurify from "dompurify"
import { Badge, Button, LoadingIndicator } from "frappe-ui"
import { ChevronRight, FileText, History, ListChecks, X } from "lucide-vue-next"
import { marked } from "marked"
import { computed } from "vue"

import AccordionCard from "@/components/AccordionCard.vue"
import CheckRow from "@/components/CheckRow.vue"
import type {
	AssignmentDay,
	CheckResult,
	DayState,
	DaySubmission,
} from "@/types"

const props = defineProps<{
	day: AssignmentDay
	dayState: DayState
	index: number
	defaultOpen: boolean
	connected: boolean
	isGrading: boolean
}>()

defineEmits<(e: "grade", name: string) => void>()

const renderedDetails = computed(() =>
	props.day.assignment_details
		? DOMPurify.sanitize(
				marked.parse(props.day.assignment_details, { async: false }) as string,
			)
		: "",
)

function formatTime(s: string): string {
	const d = new Date(s)
	return Number.isNaN(d.getTime()) ? s : d.toLocaleString()
}

function failedResults(s: DaySubmission): CheckResult[] {
	return (s.results ?? []).filter((r) => !r.passed)
}
</script>
