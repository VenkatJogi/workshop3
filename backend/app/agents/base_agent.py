import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pydantic import BaseModel
from app.models.workflow_state import AgentExecution, SupplyChainWorkflowState
from app.services.event_service import EventService
from app.services.gemini_service import GeminiService
logger=logging.getLogger(__name__)
class BaseAgent(ABC):
    name: str; description: str; output_model: type[BaseModel]
    def __init__(self,gemini_service:GeminiService,event_service:EventService): self.gemini_service=gemini_service; self.event_service=event_service
    @abstractmethod
    async def generate(self,state:SupplyChainWorkflowState,additional_context:dict|None=None)->BaseModel: raise NotImplementedError
    async def run(self,state,additional_context=None):
        started=datetime.now(timezone.utc); revision=int((additional_context or {}).get("revision_number",0))
        execution=AgentExecution(agent_name=self.name,status="RUNNING",started_at=started,revision_number=revision); state.agent_executions[self.name]=execution
        await self.event_service.publish(state,"agent_started",f"{self.name.replace('_',' ').title()} Agent started.",self.name,{"revision":revision})
        try:
            result=await self.generate(state,additional_context); execution.status="COMPLETED"; execution.completed_at=datetime.now(timezone.utc); execution.duration_seconds=(execution.completed_at-started).total_seconds()
            await self.event_service.publish(state,"agent_completed",f"{self.name.replace('_',' ').title()} Agent completed analysis.",self.name,{"duration_seconds":execution.duration_seconds,"revision":revision}); return result
        except Exception as exc:
            execution.status="FAILED"; execution.error=str(exc); execution.completed_at=datetime.now(timezone.utc); execution.duration_seconds=(execution.completed_at-started).total_seconds()
            logger.exception("Agent failed",extra={"workflow_id":state.workflow_id,"agent":self.name}); await self.event_service.publish(state,"agent_failed",f"{self.name.title()} Agent failed: {exc}",self.name); raise
