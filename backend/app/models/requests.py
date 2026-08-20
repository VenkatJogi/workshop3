from pydantic import BaseModel
class SampleWorkflowRequest(BaseModel):
    business_objective: str = "Prevent stockouts while prioritizing high-priority customer orders and minimizing cost."
    demo_conflict_mode: bool = False
