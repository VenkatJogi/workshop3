from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import PlannerOutput
class PlannerAgent(BaseAgent):
    name="planner"; description="Selects relevant analytical agents from available datasets."; output_model=PlannerOutput
    async def generate(self,state,additional_context=None):
        selected=[]
        if state.inventory_data: selected.append("inventory")
        if state.orders_data: selected.extend(["orders","demand"])
        if state.suppliers_data: selected.append("supplier")
        if state.inventory_data and state.suppliers_data: selected.append("cost_impact")
        return PlannerOutput(business_problem=state.business_objective,selected_agents=selected,decision_criteria=["High-priority order fulfillment","Stockout horizon","Supplier lead time","Incremental cost","Supplier reliability"])
