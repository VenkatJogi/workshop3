import type { WorkflowEvent } from '../types/workflow'
import { wsUrl } from './api'

const TERMINAL_EVENTS = new Set(['workflow_completed', 'human_review_required', 'agent_failed'])

export function connectWorkflow(id: string, onEvent: (event: WorkflowEvent) => void, onReconnect: () => void) {
  let socket: WebSocket | undefined
  let stopped = false
  let retry = 0
  let reconnectTimer: ReturnType<typeof setTimeout> | undefined

  const connect = () => {
    if (stopped) return
    socket = new WebSocket(wsUrl(id))
    socket.onopen = () => { retry = 0 }
    socket.onmessage = message => {
      const event = JSON.parse(message.data) as WorkflowEvent
      if (TERMINAL_EVENTS.has(event.event)) stopped = true
      onEvent(event)
      if (stopped && socket?.readyState === WebSocket.OPEN) socket.close(1000, 'Workflow complete')
    }
    socket.onclose = () => {
      if (stopped || retry >= 5) return
      retry += 1
      reconnectTimer = setTimeout(() => {
        if (stopped) return
        onReconnect()
        connect()
      }, Math.min(1000 * 2 ** retry, 10000))
    }
  }

  connect()
  return () => {
    stopped = true
    if (reconnectTimer) clearTimeout(reconnectTimer)
    socket?.close()
  }
}
