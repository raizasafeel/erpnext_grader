import type {
  AssignmentSection, CheckGroup, CheckResult, OverallStats,
  SectionState, SectionStatus, SectionSubmission,
} from '@/types'

export function statusOf(passed: number, total: number): SectionStatus {
  if (total > 0 && passed === total) return 'passed'
  if (passed > 0) return 'partial'
  return 'failed'
}

export function groupByTitle(results: CheckResult[]): CheckGroup[] {
  const order: string[] = []
  const map = new Map<string, CheckResult[]>()
  for (const r of results) {
    const key = r.title || ''
    if (!map.has(key)) { map.set(key, []); order.push(key) }
    map.get(key)!.push(r)
  }
  return order.map((title) => ({ title, checks: map.get(title)! }))
}

export function buildSectionStates(
  sections: AssignmentSection[],
  submissions: SectionSubmission[],
): SectionState[] {
  const latestBySection = new Map<string, SectionSubmission>()
  for (const s of submissions) {
    // submissions arrive newest-first; keep the first seen per section
    if (!latestBySection.has(s.section)) latestBySection.set(s.section, s)
  }
  return sections.map((section) => {
    const latest = latestBySection.get(section.name) ?? null
    const results = latest?.results ?? []
    const total = latest ? latest.total_checks : section.total_checks
    const passed = latest ? latest.passed_checks : 0
    return {
      section,
      latest,
      status: statusOf(passed, total),
      passed,
      total,
      groups: groupByTitle(results),
    }
  })
}

export function overallStats(states: SectionState[]): OverallStats {
  let secPassed = 0, chkPassed = 0, chkTotal = 0
  for (const st of states) {
    chkPassed += st.passed
    chkTotal += st.total
    if (st.status === 'passed') secPassed += 1
  }
  return { secPassed, secTotal: states.length, chkPassed, chkTotal }
}
