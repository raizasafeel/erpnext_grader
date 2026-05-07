<template>
	<div class="flex min-h-screen flex-col bg-surface-gray-1">
		<AppHeader
			:connected="connected"
			@open-details="detailsOpen = true"
			@logout="logout.submit()"
		/>

		<SiteDetailsDialog
			v-model="detailsOpen"
			:site-url="siteUrl"
			:last-checked="lastChecked"
			@disconnected="portalContext.fetch()"
		/>

		<div v-if="!connected" class="flex flex-1 items-center justify-center p-6">
			<ConnectSitePanel :default-site="siteUrl" @connected="portalContext.fetch()" />
		</div>
		<div v-else class="flex flex-1 flex-col m-6 gap-3">
			<div
				v-if="assignmentsResource.loading"
				class="rounded-md border border-outline-gray-2 bg-surface-white p-4 text-sm text-ink-gray-6"
			>
				Loading assignments...
			</div>

			<div
				v-else-if="!days.length"
				class="rounded-md border border-outline-gray-2 bg-surface-white p-4 text-sm text-ink-gray-6"
			>
				No assignments published yet.
			</div>

			<DayCard
				v-for="(day, i) in days"
				:key="day.name"
				:day="day"
				:day-state="dayStates[i]!"
				:index="i + 1"
				:default-open="i === firstUnlockedIdx"
				:connected="connected"
				:is-grading="gradingDay === day.name"
				@grade="runGrade"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import { createResource, toast } from "frappe-ui"
import { computed, ref } from "vue"

import AppHeader from "@/components/AppHeader.vue"
import ConnectSitePanel from "@/components/ConnectSitePanel.vue"
import DayCard from "@/components/DayCard.vue"
import SiteDetailsDialog from "@/components/SiteDetailsDialog.vue"
import type { AssignmentDay, DayState, DaySubmission } from "@/types"

type PortalContext = {
	user: string
	full_name: string
	course: string
	site: {
		name: string
		site: string
		last_checked: string
		connected: boolean
	} | null
}

const portalContext = createResource({
	url: "erpnext_grader.erpnext_grader.api.get_current_user_info",
	auto: true,
})

const assignmentsResource = createResource({
	url: "erpnext_grader.erpnext_grader.api.get_assignments",
	auto: true,
})

const submissionsResource = createResource({
	url: "erpnext_grader.erpnext_grader.api.get_my_submissions",
	auto: true,
})

const gradeDay = createResource({
	url: "erpnext_grader.erpnext_grader.api.grade_day",
})

const logout = createResource({
	url: "logout",
	onSuccess() {
		window.location.href = "/login"
	},
})

const context = computed(() => portalContext.data as PortalContext | null)
const days = computed(
	() => (assignmentsResource.data as AssignmentDay[] | null) ?? [],
)
const submissions = computed(
	() => (submissionsResource.data as DaySubmission[] | null) ?? [],
)

const siteUrl = computed(() => context.value?.site?.site ?? "")
const connected = computed(() => !!context.value?.site?.connected)
const lastChecked = computed(() => context.value?.site?.last_checked ?? null)

function newestFirst(a: DaySubmission, b: DaySubmission): number {
	return (
		new Date(b.submission_time).getTime() -
		new Date(a.submission_time).getTime()
	)
}

function pickBest(subs: DaySubmission[]): DaySubmission | null {
	let best: DaySubmission | null = null
	for (const sub of subs) {
		if (!best || sub.percent > best.percent) best = sub
	}
	return best
}

function badgeFor(best: DaySubmission | null): {
	theme: DayState["badgeTheme"]
	label: string | null
} {
	if (!best) return { theme: "gray", label: null }
	const passed = best.status === "Passed"
	return {
		theme: passed ? "green" : "red",
		label: `${passed ? "Passed" : "Failed"} · ${best.passed_checks}/${best.total_checks}`,
	}
}

function subtitleFor(
	locked: boolean,
	isConnected: boolean,
	prev: AssignmentDay | null,
): string | null {
	if (!locked) return null
	if (!isConnected) return "Connect your site to start"
	return `Finish Day ${prev?.day} to unlock`
}

const dayStates = computed<DayState[]>(() => {
	const byDay = new Map<string, DaySubmission[]>()
	for (const sub of submissions.value) {
		const list = byDay.get(sub.day) ?? []
		list.push(sub)
		byDay.set(sub.day, list)
	}
	for (const list of byDay.values()) list.sort(newestFirst)

	const states: DayState[] = []
	let prevPassed = true

	for (const [idx, day] of days.value.entries()) {
		const mine = byDay.get(day.name) ?? []
		const best = pickBest(mine)
		const passed = best?.status === "Passed"
		const locked = !connected.value || (idx > 0 && !prevPassed)

		const status: DayState["status"] = passed
			? "done"
			: locked
				? "locked"
				: "active"
		const { theme: badgeTheme, label: badgeLabel } = badgeFor(best)
		const subtitle = subtitleFor(
			locked,
			connected.value,
			days.value[idx - 1] ?? null,
		)

		states.push({
			day,
			submissions: mine,
			best,
			passed,
			locked,
			badgeTheme,
			badgeLabel,
			subtitle,
			status,
		})

		prevPassed = passed
	}

	return states
})

const firstUnlockedIdx = computed(() =>
	dayStates.value.findIndex((s) => !s.locked),
)

const detailsOpen = ref(false)
const gradingDay = ref<string | null>(null)

function gradingHistory(name: string): number {
	return submissions.value.filter((s) => s.day === name).length
}

async function runGrade(name: string) {
	if (gradingDay.value) return
	gradingDay.value = name
	try {
		await gradeDay.submit({ day: name })
		const temp = gradingHistory(name)
		const deadline = Date.now() + 60_000 // give up after 60s
		while (Date.now() < deadline) {
			await new Promise((r) => setTimeout(r, 2000)) //recheck every 2s
			await submissionsResource.reload()
			if (gradingHistory(name) > temp) break
		}
	} catch (e) {
		const err = e as { messages: string[]; message: string }
		toast.error(err?.messages?.[0] || err?.message || "Grading failed")
	} finally {
		gradingDay.value = null
	}
}
</script>
