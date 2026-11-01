// How each ledger action reads in activity lists.
export const ACTIONS = {
  github_issue_opened: { label: 'Opened issue', icon: 'lucide-circle-dot' },
  github_pr_merged: { label: 'Merged pull request', icon: 'lucide-git-merge' },
  github_pr_reviewed: { label: 'Reviewed pull request', icon: 'lucide-eye' },
  discuss_solution: { label: 'Accepted solution', icon: 'lucide-circle-check' },
  event_attended: { label: 'Attended', icon: 'lucide-ticket' },
  event_talk: { label: 'Gave a talk', icon: 'lucide-mic' },
  school_certification: { label: 'Earned certification', icon: 'lucide-graduation-cap' },
  request_upvote_received: { label: 'Upvote on request', icon: 'lucide-chevron-up' },
}

export function actionMeta(action) {
  return ACTIONS[action] ?? { label: action, icon: 'lucide-circle' }
}

export function repoOf(externalId) {
  return externalId?.includes('#') ? externalId.split('#')[0] : null
}

const HIGHLIGHTS = [
  ['github_pr_merged', 'PR', 'PRs'],
  ['github_pr_reviewed', 'review', 'reviews'],
  ['github_issue_opened', 'issue', 'issues'],
  ['discuss_solution', 'solution', 'solutions'],
  ['event_talk', 'talk', 'talks'],
  ['school_certification', 'certification', 'certifications'],
]

// "4 PRs · 2 solutions" — the biggest few things someone did, for one-line summaries.
export function highlights(counts, limit = 3) {
  return HIGHLIGHTS.filter(([action]) => counts[action])
    .map(([action, one, many]) => `${counts[action]} ${counts[action] === 1 ? one : many}`)
    .slice(0, limit)
    .join(' · ')
}
