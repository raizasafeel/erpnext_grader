<template>
	<details
		class="group/card rounded-md border border-outline-gray-2 bg-surface-white"
		:class="{ 'opacity-60': locked }"
		:open="open"
	>
		<summary
			class="flex items-center justify-between gap-3 p-4"
			:tabindex="locked ? -1 : 0"
		>
			<div class="flex items-center gap-3">
				<span
					class="flex size-7 shrink-0 items-center justify-center rounded-full text-p-xs font-medium"
					:class="iconClasses"
				>
					<Lock v-if="locked" class="size-3.5" />
					<Check v-else-if="status === 'done'" class="size-3.5" />
					<span v-else>{{ index }}</span>
				</span>

				<h3 class="text-p-lg font-medium text-ink-gray-9">
					{{ title }}
				</h3>
			</div>
			<div class="flex items-center gap-3">
				<Badge v-if="badgeLabel" :theme="badgeTheme">
					{{ badgeLabel }}
				</Badge>
				<ChevronRight
					v-if="!locked"
					class="size-4 shrink-0 text-ink-gray-5 transition-transform group-open/card:rotate-90"
				/>
			</div>
		</summary>

		<div v-if="!locked" class="border-t border-outline-gray-1 p-4">
			<slot />
		</div>
	</details>
</template>

<script setup lang="ts">
import { Badge } from "frappe-ui"
import { Check, ChevronRight, Lock } from "lucide-vue-next"
import { computed } from "vue"

const props = defineProps<{
	index: number | string
	title: string
	status?: "active" | "done" | "locked"
	open?: boolean
	badgeLabel?: string | null
}>()

const locked = computed(() => props.status === "locked")

const iconClasses = computed(() => {
	if (locked.value) return "bg-surface-gray-2 text-ink-gray-5"
	if (props.status === "done") return "bg-surface-green-2 text-ink-green-3"
	if (props.status === "active") return "bg-surface-gray-7 text-ink-white"
	return "bg-surface-gray-2 text-ink-gray-7"
})

const badgeTheme = computed<"green" | "red" | "gray">(() => {
	if (props.badgeLabel?.startsWith("Passed")) return "green"
	if (props.badgeLabel?.startsWith("Failed")) return "red"
	return "gray"
})
</script>
