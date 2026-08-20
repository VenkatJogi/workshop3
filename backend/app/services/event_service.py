import asyncio
from collections import defaultdict
from app.models.workflow_state import DecisionWorkflowState, WorkflowEvent


class EventService:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[WorkflowEvent]]] = defaultdict(set)

    async def publish(self, state: DecisionWorkflowState, event: str, message: str, agent: str | None = None, metadata: dict | None = None) -> WorkflowEvent:
        item = WorkflowEvent(event=event, agent=agent, message=message, metadata=metadata or {})
        state.execution_log.append(item)
        for queue in list(self._subscribers[state.workflow_id]):
            await queue.put(item)
        return item

    def subscribe(self, workflow_id: str) -> asyncio.Queue[WorkflowEvent]:
        queue: asyncio.Queue[WorkflowEvent] = asyncio.Queue()
        self._subscribers[workflow_id].add(queue)
        return queue

    def unsubscribe(self, workflow_id: str, queue: asyncio.Queue[WorkflowEvent]) -> None:
        self._subscribers[workflow_id].discard(queue)


event_service = EventService()
