import asyncio
from app.models.workflow_state import DecisionWorkflowState


class WorkflowStore:
    def __init__(self) -> None:
        self._states: dict[str, DecisionWorkflowState] = {}
        self._lock = asyncio.Lock()

    async def create(self, state: DecisionWorkflowState) -> None:
        async with self._lock:
            self._states[state.workflow_id] = state

    def get(self, workflow_id: str) -> DecisionWorkflowState | None:
        return self._states.get(workflow_id)


workflow_store = WorkflowStore()
