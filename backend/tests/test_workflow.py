import pytest
from app.orchestration.workflow import WorkflowOrchestrator

@pytest.mark.asyncio
async def test_demo_conflict_is_revised_and_completes(state, services):
    await WorkflowOrchestrator(*services).execute(state)
    assert state.workflow_status == "COMPLETED"
    assert state.revision_count == 1
    assert {item.agent_name for item in state.revision_history} == {"supplier", "cost_impact"}
    assert state.critic_review["decision"] == "APPROVE"
    assert state.action_plan["immediate_actions"]
    assert not [event for event in state.execution_log if event.event == "agent_failed"]
