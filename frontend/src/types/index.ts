export type AssignmentDay = {
	name: string
	day: number
	total_checks: number
	assignment_details: string | null
}

export type CheckResult = {
	label: string
	passed: boolean
	expected: string | null
	actual: string | null
}

export type DaySubmission = {
	name: string
	day: string
	submission_time: string
	status: "Passed" | "Failed"
	passed_checks: number
	total_checks: number
	percent: number
	results: CheckResult[]
}

export type DayState = {
	day: AssignmentDay
	submissions: DaySubmission[]
	best: DaySubmission | null
	passed: boolean
	locked: boolean
	badgeTheme: "green" | "red" | "gray"
	badgeLabel: string | null
	subtitle: string | null
	status: "active" | "done" | "locked"
}
