import pandas as pd
from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import OrderRisk,OrdersOutput
class OrdersAgent(BaseAgent):
    name="orders"; description="Aggregates pending demand and identifies customer orders at risk."; output_model=OrdersOutput
    async def generate(self,state,additional_context=None):
        frame=pd.DataFrame(state.orders_data); pending=frame[frame["status"].str.upper()=="PENDING"].copy(); summary=pending.groupby(["product_id","product_name"],as_index=False)["quantity"].sum().rename(columns={"quantity":"pending_quantity"})
        stock={str(x["product_id"]):float(x["current_stock"]) for x in state.inventory_data}; demand={str(x.product_id):float(x.pending_quantity) for x in summary.itertuples()}; risks=[]
        for row in pending.itertuples():
            shortage=demand[str(row.product_id)]>stock.get(str(row.product_id),0); priority=str(row.priority).upper(); level="CRITICAL" if shortage and priority=="HIGH" else "HIGH" if shortage else "MEDIUM" if priority=="HIGH" else "LOW"
            if level!="LOW": risks.append(OrderRisk(order_id=str(row.order_id),customer=str(row.customer),product_id=str(row.product_id),product_name=str(row.product_name),quantity=float(row.quantity),priority=priority,risk_level=level,reason="Aggregate pending demand exceeds current stock." if shortage else "High-priority order consumes constrained inventory."))
        high_priority_risks=[item for item in risks if item.priority=="HIGH"]
        return OrdersOutput(total_pending_orders=len(pending),high_priority_orders=int((pending["priority"].str.upper()=="HIGH").sum()),orders_at_risk=risks,high_priority_orders_at_risk=high_priority_risks,product_demand_summary=summary.to_dict(orient="records"),key_findings=[f"{len(risks)} orders require attention.",f"{len(high_priority_risks)} high-priority orders are at risk.",f"Pending demand spans {len(summary)} products."],confidence_score=.98)
