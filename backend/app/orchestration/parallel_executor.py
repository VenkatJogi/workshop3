import asyncio
from app.orchestration.agent_registry import get_agent_class,RESULT_FIELDS
class ParallelExecutor:
    def __init__(self,gemini,events): self.gemini=gemini; self.events=events
    async def run(self,selected_agents,state):
        await self.events.publish(state,"parallel_execution_started",f"Running {len(selected_agents)} supply-chain specialists in parallel.",metadata={"agents":selected_agents})
        results=await asyncio.gather(*(get_agent_class(name)(self.gemini,self.events).run(state) for name in selected_agents),return_exceptions=True)
        for name,result in zip(selected_agents,results):
            if not isinstance(result,Exception): setattr(state,RESULT_FIELDS[name],result.model_dump())
        await self.events.publish(state,"parallel_execution_completed","Parallel business analysis completed.",metadata={"successful":[name for name,result in zip(selected_agents,results) if not isinstance(result,Exception)]}); return results
