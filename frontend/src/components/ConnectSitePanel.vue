<template>
	<div class="rounded-md border border-outline-gray-2 bg-surface-white p-6">
		<h3 class="text-p-lg font-medium text-ink-gray-9 mb-3">Connect your ERPNext site</h3>
		<form class="flex flex-col gap-3" @submit.prevent="submit">
			<FormControl
				v-model="siteInput"
				type="text"
				placeholder="https://your-site.m.frappe.cloud"
				:readonly="!!defaultSite"
			/>
			<ol class="list-decimal flex flex-col gap-1 pl-5 text-p-sm text-ink-gray-7">
				<li>Your ERPNext site must be signed in with the same email as this portal.</li>
				<li>Enter the URL above and click Connect.</li>
			</ol>
			<Button
				variant="solid"
				:loading="registerSite.loading"
				type="submit"
				class="w-full mt-3"
			>
				Connect
			</Button>
			<p v-if="defaultSite" class="text-p-xs text-ink-gray-6">
				To connect a different site, contact
				<a
					href="mailto:school@frappe.io"
					class="text-ink-blue-3 hover:underline"
				>school@frappe.io</a>.
			</p>
			<ErrorMessage
				v-if="registerSite.error"
				:message="registerSite.error.messages?.[0] || 'Failed to connect'"
			/>
		</form>
	</div>
</template>

<script setup lang="ts">
import { Button, ErrorMessage, FormControl, createResource } from "frappe-ui"
import { ref, watch } from "vue"

const props = defineProps<{
	defaultSite: string
}>()

const emit = defineEmits<(e: "connected") => void>()

const registerSite = createResource({
	url: "erpnext_grader.erpnext_grader.api.register_site",
})

const siteInput = ref("")
watch(
	() => props.defaultSite,
	(v) => {
		if (v && !siteInput.value) siteInput.value = v
	},
	{ immediate: true },
)

async function submit() {
	const url = siteInput.value.trim()
	if (!url) return
	// Belt-and-suspenders: the input is readonly when defaultSite is set,
	// but if it ever gets bypassed we still don't submit a mismatched URL —
	// the backend rejects this case with a "contact support" error.
	if (props.defaultSite && url !== props.defaultSite.trim()) return
	await registerSite.submit({ site: url })
	emit("connected")
}
</script>
