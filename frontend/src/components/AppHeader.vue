<template>
	<header
		class="flex items-center justify-between gap-4 border-b border-outline-gray-2 bg-surface-white px-6 py-3"
	>
		<a href="/lms" class="flex items-center">
			<img :src="logoSrc" alt="Frappe School" class="h-7 w-auto" />
		</a>
		<div class="flex items-center gap-1">
			<Tooltip v-if="connected" text="Site details">
				<Button variant="ghost" aria-label="Site details" @click="$emit('open-details')">
					<template #icon><Plug class="size-4 text-ink-gray-7" /></template>
				</Button>
			</Tooltip>
			<Tooltip text="Sign out">
				<Button variant="ghost" aria-label="Sign out" @click="$emit('logout')">
					<template #icon><LogOut class="size-4 text-ink-gray-7" /></template>
				</Button>
			</Tooltip>
		</div>
	</header>
</template>

<script setup lang="ts">
import { Button, Tooltip, createResource } from "frappe-ui"
import { LogOut, Plug } from "lucide-vue-next"
import { computed } from "vue"

defineProps<{
	connected: boolean
}>()

defineEmits<{
	(e: "open-details"): void
	(e: "logout"): void
}>()

type Branding = {
	banner_image?: { file_url?: string }
	app_logo?: { file_url?: string }
}

const branding = createResource({
	url: "lms.lms.api.get_branding",
	auto: true,
})

const logoSrc = computed(() => {
	const data = branding.data as Branding | null
	return (
		data?.banner_image?.file_url ||
		data?.app_logo?.file_url ||
		"/assets/lms/images/lms-logo.png"
	)
})
</script>
