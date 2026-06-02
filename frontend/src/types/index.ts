export interface AssignmentSection {
  name: string
  section: string
  section_order: number
  blurb: string | null
  total_checks: number
  assignment_details: string | null
}

export interface CheckResult {
  label: string
  passed: boolean
  expected: string | null
  actual: string | null
  section: string
  title: string
}

export interface SectionSubmission {
  name: string
  section: string
  submission_time: string
  status: 'Passed' | 'Failed'
  passed_checks: number
  total_checks: number
  percent: number
  results: CheckResult[]
}

export type SectionStatus = 'passed' | 'partial' | 'failed'

export interface CheckGroup {
  title: string
  checks: CheckResult[]
}

export interface SectionState {
  section: AssignmentSection
  latest: SectionSubmission | null
  status: SectionStatus
  passed: number
  total: number
  groups: CheckGroup[]
}

export interface OverallStats {
  secPassed: number
  secTotal: number
  chkPassed: number
  chkTotal: number
}
