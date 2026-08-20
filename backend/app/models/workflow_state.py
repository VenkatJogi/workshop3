from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field

def utc_now(): return datetime.now(timezone.utc)
class AgentExecution(BaseModel):
    agent_name: str; status: str = "IDLE"; started_at: datetime | None = None
    completed_at: datetime | None = None; duration_seconds: float | None = None
    revision_number: int = 0; error: str | None = None
class WorkflowEvent(BaseModel):
    timestamp: datetime = Field(default_factory=utc_now); event: str
    agent: str | None = None; message: str; metadata: dict[str, Any] = Field(default_factory=dict)
class AgentRevision(BaseModel):
    agent_name: str; revision_number: int; previous_output: dict; revised_output: dict
    reason: str; timestamp: datetime = Field(default_factory=utc_now)
class SupplyChainWorkflowState(BaseModel):
    workflow_id: str; business_objective: str
    inventory_data: list[dict] = Field(default_factory=list); orders_data: list[dict] = Field(default_factory=list)
    suppliers_data: list[dict] = Field(default_factory=list); file_validations: list[dict] = Field(default_factory=list)
    demo_conflict_mode: bool = False; data_summary: dict | None = None; plan: dict | None = None
    selected_agents: list[str] = Field(default_factory=list)
    inventory_analysis: dict | None = None; orders_analysis: dict | None = None
    demand_analysis: dict | None = None; supplier_analysis: dict | None = None; cost_analysis: dict | None = None
    proposed_decision: dict | None = None; critic_review: dict | None = None; action_plan: dict | None = None
    revision_count: int = 0; max_revisions: int = 2; workflow_status: str = "INITIALIZED"
    agent_executions: dict[str, AgentExecution] = Field(default_factory=dict)
    execution_log: list[WorkflowEvent] = Field(default_factory=list)
    revision_history: list[AgentRevision] = Field(default_factory=list); unresolved_issues: list[str] = Field(default_factory=list)
DecisionWorkflowState = SupplyChainWorkflowState
