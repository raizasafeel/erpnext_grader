<template>
	<div class="rounded-md border border-outline-gray-2 bg-surface-white p-6">
		<h3 class="text-lg font-medium text-ink-gray-9 mb-3">Connect your ERPNext site</h3>
		<form class="flex flex-col gap-3" @submit.prevent="submit">
			<FormControl
				v-model="siteInput"
				type="text"
				placeholder="https://your-site.m.frappe.cloud"
			/>
			<ol class="list-decimal flex flex-col gap-1 pl-5 text-sm text-ink-gray-7">
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
	if (!siteInput.value.trim()) return
	await registerSite.submit({ site: siteInput.value.trim() })
	emit("connected")
}
</script>
