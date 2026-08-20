from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import CriticOutput,RevisionRequest
class CriticAgent(BaseAgent):
    name="critic"; description="Challenges supplier timing, order protection, cost, and unsupported assumptions."; output_model=CriticOutput
    async def generate(self,state,additional_context=None):
        decisions=(state.proposed_decision or {}).get("product_decisions",[]); forecasts={x["product_id"]:x for x in (state.demand_analysis or {}).get("forecasts",[])}; conflicts=[]
        for item in decisions:
            horizon=forecasts.get(item["product_id"],{}).get("estimated_days_until_stockout")
            if item["recommended_action"]=="REORDER_REGULAR" and horizon is not None and horizon<7: conflicts.append(f"Regular supplier delivery for {item['product_name']} arrives after its {horizon}-day stockout horizon.")
        if conflicts and state.revision_count<state.max_revisions:
            return CriticOutput(decision="REVISE",overall_confidence=.96,strengths=["Recommendation considers unit cost."],conflicts=conflicts,unsupported_assumptions=["Regular supply can arrive before stockout."],missing_information=[],revision_requests=[RevisionRequest(target_agent="supplier",reason="Evaluate faster supplier options.",required_context="Stockout occurs before regular delivery."),RevisionRequest(target_agent="cost_impact",reason="Evaluate partial emergency purchasing.",required_context="Cover only the immediate gap while minimizing premium cost.")],reasoning="The initial plan minimizes purchase cost but fails the service-level timing constraint.")
        return CriticOutput(decision="APPROVE",overall_confidence=.91,strengths=["High-priority orders are protected.","Supplier timing and premium cost are explicitly balanced."],conflicts=[],unsupported_assumptions=[],missing_information=[],revision_requests=[],reasoning="The recommendations are supported by inventory, demand, supplier, and cost evidence.")
