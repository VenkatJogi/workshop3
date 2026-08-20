import { Bot, Gauge, GitPullRequestArrow, Radio } from 'lucide-react'
import type { FinalResult, WorkflowStatus } from '../types/workflow'

export function WorkflowSummary({ status, result }: { status?: WorkflowStatus; result?: FinalResult }) {
  const confidence = result ? `${Math.round(result.decision.confidence_score * 100)}%` : '—'
  const items = [
    { label: 'Workflow status', value: status?.status.replaceAll('_', ' ') || 'READY', icon: Radio, color: 'text-mint', glow: 'bg-mint/10' },
    { label: 'Active specialists', value: String(status?.selected_agents.length || 0).padStart(2, '0'), icon: Bot, color: 'text-sky-300', glow: 'bg-sky-400/10' },
    { label: 'Revision cycles', value: String(status?.revision_count || 0).padStart(2, '0'), icon: GitPullRequestArrow, color: 'text-amber', glow: 'bg-amber/10' },
    { label: 'Decision confidence', value: confidence, icon: Gauge, color: 'text-violet-300', glow: 'bg-violet-400/10' },
  ]
  return <div className="mb-4 grid grid-cols-2 gap-2 lg:grid-cols-4">
    {items.map(({ label, value, icon: Icon, color, glow }) => <div key={label} className="glass flex items-center gap-3 rounded-xl px-3 py-2.5">
      <span className={`grid h-9 w-9 place-items-center rounded-lg ${glow} ${color}`}><Icon size={17}/></span>
      <div className="min-w-0"><p className="truncate text-[9px] font-semibold uppercase tracking-[.16em] text-slate-500">{label}</p><p className={`mt-0.5 truncate font-display text-sm font-semibold ${color}`}>{value}</p></div>
    </div>)}
  </div>
}
