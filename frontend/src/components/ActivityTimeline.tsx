import { AlertTriangle, CheckCircle2, Circle, GitBranch, LoaderCircle } from 'lucide-react'
import type { WorkflowEvent } from '../types/workflow'

export function ActivityTimeline({ events }: { events: WorkflowEvent[] }) {
  return <section className="glass flex min-h-[680px] min-w-0 flex-col overflow-hidden rounded-2xl">
    <div className="border-b border-white/10 px-4 py-3"><p className="font-display text-sm font-semibold">Live activity</p><p className="text-[11px] text-slate-500">{events.length ? `${events.length} events received` : 'Waiting for a workflow'}</p></div>
    <div className="scrollbar min-h-0 flex-1 overflow-y-auto p-4"><div className="relative space-y-5 before:absolute before:bottom-3 before:left-[7px] before:top-3 before:w-px before:bg-white/10">
      {events.length === 0 ? <div className="py-20 text-center text-xs text-slate-600">Agent activity will appear here.</div> : events.map((event, index) => {
        const conflict = event.event === 'conflict_detected'
        const done = event.event.includes('completed') || event.event === 'agent_revised'
        const Icon = conflict ? AlertTriangle : event.event.includes('routed') ? GitBranch : done ? CheckCircle2 : index === events.length - 1 ? LoaderCircle : Circle
        return <div key={`${event.timestamp}-${index}`} className="relative flex gap-3"><span className={`z-10 mt-0.5 grid h-4 w-4 place-items-center rounded-full bg-panel ${conflict ? 'text-amber' : done ? 'text-mint' : 'text-sky-300'}`}><Icon size={13} className={index === events.length - 1 && !done ? 'animate-spin' : ''}/></span><div className="min-w-0 flex-1"><div className="flex items-center justify-between gap-2"><span className="truncate text-[10px] font-semibold uppercase tracking-wider text-slate-500">{event.event.replaceAll('_', ' ')}</span><time className="text-[9px] tabular-nums text-slate-600">{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</time></div><p className={`mt-1 text-xs leading-relaxed ${conflict ? 'text-amber' : 'text-slate-300'}`}>{event.message}</p></div></div>
      })}
    </div></div>
  </section>
}
