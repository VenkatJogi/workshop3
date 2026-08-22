import pytest
from app.agents.data_ingestion_agent import DataIngestionAgent
from app.agents.decision_agent import DecisionAgent, ground_cited_orders
from app.models.agent_outputs import AnswerItem
from app.agents.planner_agent import PlannerAgent
from app.orchestration.parallel_executor import ParallelExecutor

@pytest.mark.asyncio
async def test_ingestion_planner_and_specialists(state, services):
    summary = await DataIngestionAgent(*services).run(state)
    state.data_summary = summary.model_dump()
    plan = await PlannerAgent(*services).run(state)
    assert set(plan.selected_agents) == {"inventory", "orders", "demand", "supplier", "cost_impact"}
    state.selected_agents = plan.selected_agents
    await ParallelExecutor(*services).run(plan.selected_agents, state)
    assert state.inventory_analysis["critical_products"]
    assert state.orders_analysis["orders_at_risk"]
    assert state.supplier_analysis["fast_delivery_options"]
    assert state.cost_analysis["product_comparisons"]

@pytest.mark.asyncio
async def test_live_decision_uses_configured_gemini_service(state, services):
    summary = await DataIngestionAgent(*services).run(state)
    state.data_summary = summary.model_dump()
    plan = await PlannerAgent(*services).run(state)
    state.selected_agents = plan.selected_agents
    await ParallelExecutor(*services).run(plan.selected_agents, state)
    state.demo_conflict_mode = False

    class FakeGemini:
        called = False
        async def generate_structured(self, _system, prompt, response_model):
            import json
            self.called = True
            baseline = json.loads(prompt.split("\n", 1)[1])["deterministic_baseline"]
            return response_model.model_validate(baseline)

    fake = FakeGemini()
    output = await DecisionAgent(fake, services[1]).run(state)
    assert fake.called
    assert output.product_decisions

@pytest.mark.asyncio
async def test_order_analysis_preserves_customer_evidence_for_dynamic_questions(state, services):
    plan = await PlannerAgent(*services).run(state)
    state.selected_agents = plan.selected_agents
    await ParallelExecutor(*services).run(plan.selected_agents, state)
    first = state.orders_analysis["orders_at_risk"][0]
    assert first["customer"] == "Customer B"
    assert first["order_id"] == "ORD001"
    priority_risks = state.orders_analysis["high_priority_orders_at_risk"]
    assert {item["order_id"] for item in priority_risks} == {"ORD001", "ORD002", "ORD016", "ORD017", "ORD023", "ORD024"}

    output = await DecisionAgent(*services).run(state)
    output.direct_answer = "Orders ORD001 and ORD002 are at risk."
    output.answer_items = [AnswerItem(title="Incorrect grouping", value="ORD001 and ORD002", evidence="High priority")]
    grounded = ground_cited_orders(output, state)
    assert [(item.title, item.value.split(" · ")[0]) for item in grounded.answer_items] == [("Customer B", "ORD001"), ("Customer C", "ORD002")]
