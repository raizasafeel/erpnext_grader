import "./index.css"

import { FrappeUI, frappeRequest, setConfig } from "frappe-ui"
import { createApp } from "vue"
import { createRouter, createWebHistory } from "vue-router"

import App from "./App.vue"

function getSessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	const user = cookies.get("user_id")
	return !user || user === "Guest" ? null : user
}

if (!getSessionUser()) {
	const target = encodeURIComponent(
		window.location.pathname + window.location.search,
	)
	window.location.href = `/login?redirect-to=${target}`
} else {
	setConfig("resourceFetcher", frappeRequest)

	const router = createRouter({
		history: createWebHistory("/assignments-portal/erpnext"),
		routes: [{ path: "/:catchAll(.*)", component: { render: () => null } }],
	})

	const app = createApp(App)
	app.use(FrappeUI)
	app.use(router)
	app.mount("#app")
}
