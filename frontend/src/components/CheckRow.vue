<template>
	<li class="flex flex-col border-b border-outline-gray-1 p-3 last:border-b-0">
		<div class="flex gap-3 items-center">
			<span
				class="flex size-4 items-center justify-center rounded-full"
				:class="indicator.bg"
			>
				<component :is="indicator.icon" :class="indicator.iconSize"
			/></span>
			<span class="text-p-base text-ink-gray-9">{{ label }}</span>
		</div>
		<dl
			v-if="state === 'fail' && detailRows.length"
			class="mt-2 flex flex-col gap-1 rounded-md bg-surface-gray-1 px-4 py-3 text-p-sm"
		>
			<div v-for="row in detailRows" :key="row.label" class="flex gap-1.5">
				<dt class="shrink-0 text-ink-gray-5">{{ row.label }}:</dt>
				<dd class="min-w-0 break-words" :class="row.class">
					{{ row.value }}
				</dd>
			</div>
		</dl>
	</li>
</template>

<script setup lang="ts">
import { Check, X } from "lucide-vue-next"
import { type Component, computed } from "vue"

type StatusIndicator = { icon: Component; bg: string; iconSize: string }

const StatusIndicatorClasses: Record<"pass" | "fail", StatusIndicator> = {
	pass: {
		icon: Check,
		bg: "bg-surface-green-2 text-ink-green-3",
		iconSize: "size-3",
	},
	fail: {
		icon: X,
		bg: "bg-surface-red-2 text-ink-red-3",
		iconSize: "size-3",
	},
}

const props = defineProps<{
	label: string
	state: "pass" | "fail"
	expected?: string | null
	actual?: string | null
}>()

const indicator = computed(() => StatusIndicatorClasses[props.state])

const detailRows = computed(() => {
	const rows: { label: string; value: string; class: string }[] = []
	if (props.expected)
		rows.push({
			label: "Expected",
			value: props.expected,
			class: "text-ink-gray-7",
		})
	if (props.actual)
		rows.push({ label: "Actual", value: props.actual, class: "text-ink-red-3" })
	return rows
})
</script>
