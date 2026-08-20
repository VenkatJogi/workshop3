from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import ActionItem,ActionPlanOutput
class ActionPlannerAgent(BaseAgent):
    name="action_planner"; description="Converts approved decisions into owned, time-bound actions."; output_model=ActionPlanOutput
    async def generate(self,state,additional_context=None):
        immediate=[]; short=[]; monitor=[]
        for item in (state.proposed_decision or {}).get("product_decisions",[]):
            if item["recommended_action"]=="PARTIAL_EMERGENCY_REORDER": immediate.append(ActionItem(priority="CRITICAL",action=f"Contact emergency supplier and cover the immediate gap for {item['product_name']}.",owner="Procurement Lead",timeline="Today",expected_outcome="Protect high-priority orders before stockout.")); short.append(ActionItem(priority="HIGH",action=f"Place regular replenishment order for {item['product_name']} safety stock.",owner="Inventory Planner",timeline="Within 24 hours",expected_outcome="Restore inventory at sustainable unit cost."))
            elif item["recommended_action"]=="REORDER_REGULAR": short.append(ActionItem(priority="HIGH",action=f"Place regular supplier order for {item['product_name']}.",owner="Procurement",timeline="Within 24 hours",expected_outcome="Replenish inventory before service degrades."))
            monitor.append(ActionItem(priority="MEDIUM",action=f"Track daily stock, pending demand, and inbound ETA for {item['product_name']}.",owner="Operations Analyst",timeline="Daily",expected_outcome="Early warning if the supply plan slips."))
        return ActionPlanOutput(immediate_actions=immediate,short_term_actions=short,monitoring_actions=monitor,business_summary="Execute urgent coverage first, replenish economically second, and monitor supplier delivery against the stockout horizon.")
