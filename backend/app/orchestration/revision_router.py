import asyncio
from app.models.workflow_state import AgentRevision
from app.orchestration.agent_registry import get_agent_class,RESULT_FIELDS
class RevisionRouter:
    def __init__(self,gemini,events): self.gemini=gemini; self.events=events
    async def process(self,requests,state):
        async def revise(request):
            if request.target_agent not in RESULT_FIELDS: raise ValueError(f"Unknown revision target: {request.target_agent}")
            field=RESULT_FIELDS[request.target_agent]; previous=getattr(state,field) or {}; await self.events.publish(state,"revision_routed",f"Revision routed to {request.target_agent.replace('_',' ').title()} Agent.","revision_router",{"target_agent":request.target_agent,"reason":request.reason})
            output=await get_agent_class(request.target_agent)(self.gemini,self.events).run(state,{"previous_output":previous,"critic_feedback":request.reason,"required_context":request.required_context,"revision_number":state.revision_count+1}); setattr(state,field,output.model_dump()); state.revision_history.append(AgentRevision(agent_name=request.target_agent,revision_number=state.revision_count+1,previous_output=previous,revised_output=output.model_dump(),reason=request.reason)); await self.events.publish(state,"agent_revised",f"{request.target_agent.replace('_',' ').title()} Agent revised its analysis.",request.target_agent)
        await asyncio.gather(*(revise(request) for request in requests))
