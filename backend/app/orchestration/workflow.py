from app.agents.data_ingestion_agent import DataIngestionAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.critic_agent import CriticAgent
from app.agents.action_planner_agent import ActionPlannerAgent
from app.orchestration.parallel_executor import ParallelExecutor
from app.orchestration.revision_router import RevisionRouter
class WorkflowOrchestrator:
    def __init__(self,gemini,events):
        self.events=events; self.ingestion=DataIngestionAgent(gemini,events); self.planner=PlannerAgent(gemini,events); self.parallel=ParallelExecutor(gemini,events); self.decision=DecisionAgent(gemini,events); self.critic=CriticAgent(gemini,events); self.router=RevisionRouter(gemini,events); self.action=ActionPlannerAgent(gemini,events)
    async def execute(self,state):
        try:
            state.workflow_status="INGESTING"; await self.events.publish(state,"workflow_started","Supply-chain workflow started."); await self.events.publish(state,"files_validated","Excel files passed schema validation.",metadata={"files":state.file_validations})
            summary=await self.ingestion.run(state); state.data_summary=summary.model_dump(); await self.events.publish(state,"data_ingestion_completed","Data relationships and quality checks completed.","data_ingestion")
            state.workflow_status="PLANNING"; plan=await self.planner.run(state); state.plan=plan.model_dump(); state.selected_agents=plan.selected_agents; await self.events.publish(state,"agents_selected",f"Planner selected {len(plan.selected_agents)} specialists.","planner",{"selected_agents":plan.selected_agents})
            state.workflow_status="ANALYZING"; await self.parallel.run(state.selected_agents,state)
            if not state.demo_conflict_mode: await self.events.publish(state,"gemini_synthesis_started",f"Live synthesis started with {self.decision.gemini_service.settings.gemini_model}.","decision",{"mode":"live_gemini"})
            decision=await self.decision.run(state); state.proposed_decision=decision.model_dump(); await self.events.publish(state,"decision_generated","Product-level business decisions generated.","decision")
            await self.events.publish(state,"critic_started","Critic is testing stockout timing, order protection, and cost.","critic"); critic=await self.critic.run(state); state.critic_review=critic.model_dump(); await self.events.publish(state,"critic_completed",f"Critic result: {critic.decision}.","critic",{"decision":critic.decision})
            while critic.decision!="APPROVE" and state.revision_count<state.max_revisions:
                if critic.conflicts: await self.events.publish(state,"conflict_detected",critic.conflicts[0],"critic",{"revision_agents":[x.target_agent for x in critic.revision_requests]})
                await self.events.publish(state,"revision_requested","Critic requested targeted supply and cost revision.","critic"); await self.router.process(critic.revision_requests,state); state.revision_count+=1
                if not state.demo_conflict_mode: await self.events.publish(state,"gemini_synthesis_started",f"Live revised synthesis started with {self.decision.gemini_service.settings.gemini_model}.","decision",{"mode":"live_gemini","revision":state.revision_count})
                decision=await self.decision.run(state); state.proposed_decision=decision.model_dump(); await self.events.publish(state,"decision_generated","Business decision regenerated after revision.","decision")
                critic=await self.critic.run(state); state.critic_review=critic.model_dump(); await self.events.publish(state,"critic_completed",f"Critic result: {critic.decision}.","critic",{"decision":critic.decision})
            if critic.decision!="APPROVE": state.workflow_status="HUMAN_REVIEW_REQUIRED"; state.unresolved_issues=critic.conflicts+critic.missing_information; await self.events.publish(state,"human_review_required","Revision limit reached; human review required."); return
            action=await self.action.run(state); state.action_plan=action.model_dump(); await self.events.publish(state,"action_plan_generated","Approved recommendations converted into an action plan.","action_planner")
            state.workflow_status="COMPLETED"; await self.events.publish(state,"workflow_completed","Supply-chain action plan completed.",metadata={"status":"COMPLETED"})
        except Exception as exc:
            state.workflow_status="FAILED"; await self.events.publish(state,"agent_failed",f"Workflow failed: {exc}")
