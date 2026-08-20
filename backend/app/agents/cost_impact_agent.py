from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import CostImpactOutput,ProductCostComparison
class CostImpactAgent(BaseAgent):
    name="cost_impact"; description="Calculates replenishment costs and emergency premiums."; output_model=CostImpactOutput
    async def generate(self,state,additional_context=None):
        stock={str(x["product_id"]):float(x["current_stock"]) for x in state.inventory_data}; pending={}
        for row in state.orders_data:
            if str(row["status"]).upper()=="PENDING": pending[str(row["product_id"])]=pending.get(str(row["product_id"]),0)+float(row["quantity"])
        comparisons=[]; regular_total=0.; emergency_total=0.
        for pid in sorted(pending):
            rows=[x for x in state.suppliers_data if str(x["product_id"])==pid]; regular=next((x for x in rows if str(x["supplier_type"]).upper()=="REGULAR"),None); emergency=next((x for x in rows if str(x["supplier_type"]).upper()=="EMERGENCY"),None); shortage=max(0,pending[pid]-stock.get(pid,0)); reg_price=float(regular["unit_price"]) if regular else None; em_price=float(emergency["unit_price"]) if emergency else None; regular_total+=(max(shortage,float(regular["minimum_order_quantity"]))*reg_price if regular and shortage else 0); emergency_total+=(max(shortage,float(emergency["minimum_order_quantity"]))*em_price if emergency and shortage else 0); premium=round((em_price/reg_price-1)*100,1) if reg_price and em_price else None
            comparisons.append(ProductCostComparison(product_id=pid,regular_supplier=regular["supplier_name"] if regular else None,regular_unit_price=reg_price,emergency_supplier=emergency["supplier_name"] if emergency else None,emergency_unit_price=em_price,premium_percentage=premium))
        additional=emergency_total-regular_total
        revised=bool(additional_context)
        return CostImpactOutput(estimated_regular_cost=regular_total,estimated_emergency_cost=emergency_total,additional_cost=additional,product_comparisons=comparisons,cost_drivers=["Replenishment shortage quantity","Supplier MOQ","Emergency price premium"],potential_savings=["Use emergency supply only for the immediate high-priority gap.","Use regular replenishment for safety stock."],tradeoffs=["Faster delivery costs more per unit.","MOQ can create surplus inventory."],recommendation="Use a partial emergency order plus regular replenishment." if revised else "Prefer regular supply except where stockout occurs before its delivery.",confidence_score=.96)
