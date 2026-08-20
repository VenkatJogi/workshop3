import json

from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import DecisionOutput, ProductDecision
from app.prompts.decision import SYSTEM_INSTRUCTION


class DecisionAgent(BaseAgent):
    name = "decision"
    description = "Synthesizes operational evidence into product-level decisions."
    output_model = DecisionOutput

    async def generate(self, state, additional_context=None):
        inventory = {item["product_id"]: item for item in state.inventory_data}
        forecasts = {item["product_id"]: item for item in (state.demand_analysis or {}).get("forecasts", [])}
        demand = {item["product_id"]: float(item["pending_quantity"]) for item in (state.orders_analysis or {}).get("product_demand_summary", [])}
        decisions = []
        for product_id, quantity in demand.items():
            row = inventory[product_id]
            stock = float(row["current_stock"])
            shortage = max(0, quantity - stock)
            horizon = forecasts.get(product_id, {}).get("estimated_days_until_stockout")
            priority = "CRITICAL" if shortage > 0 and horizon is not None and horizon < 7 else "HIGH" if shortage > 0 else "MEDIUM"
            if shortage <= 0:
                action, reasoning = "NO_ACTION_REQUIRED", "Current stock covers all pending demand."
            elif state.demo_conflict_mode and state.revision_count == 0:
                action, reasoning = "REORDER_REGULAR", "Place a regular replenishment order to minimize unit cost."
            elif horizon is not None and horizon < 7:
                action, reasoning = "PARTIAL_EMERGENCY_REORDER", "Use emergency supply for the immediate shortage and regular supply to restore safety stock."
            else:
                action, reasoning = "REORDER_REGULAR", "Regular supply can cover the replenishment requirement."
            decisions.append(ProductDecision(
                product_id=product_id, product_name=str(row["product_name"]), priority=priority,
                recommended_action=action, reasoning=reasoning,
                supporting_evidence=[f"Current stock: {stock:g}", f"Pending demand: {quantity:g}",
                                     f"Estimated stockout: {horizon} days" if horizon is not None else "Stockout horizon unavailable"],
                risks=["Supplier delivery variability", "Demand may change before delivery"],
                assumptions=["Pending orders approximate near-term demand"],
                estimated_business_impact=f"Addresses a {shortage:g}-unit immediate gap." if shortage else "No immediate shortage cost.",
            ))
        affected = [item for item in decisions if item.recommended_action != "NO_ACTION_REQUIRED"]
        baseline = DecisionOutput(
            executive_summary=f"{len(affected)} products require replenishment action to protect customer fulfillment.",
            product_decisions=decisions,
            overall_strategy="Protect high-priority demand with minimal emergency purchasing, then restore stock through regular suppliers.",
            key_tradeoffs=["Service level versus emergency premium", "Immediate availability versus supplier reliability"],
            unresolved_questions=["Confirm supplier capacity before purchase order release."], confidence_score=.88,
        )
        if state.demo_conflict_mode:
            return baseline
        context = {
            "business_objective": state.business_objective,
            "inventory_analysis": state.inventory_analysis,
            "orders_analysis": state.orders_analysis,
            "demand_analysis": state.demand_analysis,
            "supplier_analysis": state.supplier_analysis,
            "cost_analysis": state.cost_analysis,
            "deterministic_baseline": baseline.model_dump(),
        }
        return await self.gemini_service.generate_structured(
            SYSTEM_INSTRUCTION,
            "Interpret the deterministic evidence below. Keep every product, preserve all supplied quantities and costs, and return the strongest operational recommendation.\n" + json.dumps(context, default=str),
            DecisionOutput,
        )
