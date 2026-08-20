from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import InventoryAlert,InventoryOutput
class InventoryAgent(BaseAgent):
    name="inventory"; description="Calculates stock health against reorder and maximum levels."; output_model=InventoryOutput
    async def generate(self,state,additional_context=None):
        alerts=[]
        for row in state.inventory_data:
            stock=float(row["current_stock"]); reorder=float(row["reorder_level"]); maximum=float(row["maximum_stock"])
            status="CRITICAL" if stock<=reorder*.6 else "LOW" if stock<=reorder else "OVERSTOCKED" if stock>maximum else "HEALTHY"
            issue={"CRITICAL":"Stock is critically below its reorder buffer.","LOW":"Stock is at or below reorder level.","OVERSTOCKED":"Stock exceeds maximum target.","HEALTHY":"Stock is within policy limits."}[status]
            alerts.append(InventoryAlert(product_id=str(row["product_id"]),product_name=str(row["product_name"]),current_stock=stock,reorder_level=reorder,status=status,issue=issue))
        critical=[x for x in alerts if x.status=="CRITICAL"]; low=[x for x in alerts if x.status=="LOW"]; over=[x for x in alerts if x.status=="OVERSTOCKED"]
        return InventoryOutput(total_products=len(alerts),critical_products=critical,low_stock_products=low,healthy_products=sum(x.status=="HEALTHY" for x in alerts),overstocked_products=over,key_findings=[f"{len(critical)} products are critical.",f"{len(low)} additional products are below reorder level.",f"{len(over)} products exceed maximum stock."],confidence_score=.99)
