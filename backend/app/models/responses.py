from pydantic import BaseModel
class CreateWorkflowResponse(BaseModel): workflow_id: str; status: str = "STARTED"
class HealthResponse(BaseModel): status: str = "healthy"
