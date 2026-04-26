<script setup lang="ts">
import { FrappeUIProvider } from "frappe-ui"

import StudentView from "@/pages/StudentView.vue"
</script>

<template>
	<FrappeUIProvider>
		<StudentView />
	</FrappeUIProvider>
</template>
