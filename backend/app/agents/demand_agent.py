from datetime import timedelta
import pandas as pd
from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import DemandForecast,DemandOutput
class DemandAgent(BaseAgent):
    name="demand"; description="Calculates transparent demand rates, trends, and stockout horizons."; output_model=DemandOutput
    async def generate(self,state,additional_context=None):
        frame=pd.DataFrame(state.orders_data); frame["order_date"]=pd.to_datetime(frame["order_date"]); stock={str(x["product_id"]):float(x["current_stock"]) for x in state.inventory_data}; forecasts=[]
        for (pid,name),group in frame.groupby(["product_id","product_name"]):
            start=group["order_date"].min().to_pydatetime(); end=group["order_date"].max().to_pydatetime(); days=max(1,(end-start).days+1); avg=float(group["quantity"].sum())/days; midpoint=pd.Timestamp(start+timedelta(hours=days*12)); first=float(group[group["order_date"]<midpoint]["quantity"].sum()); second=float(group[group["order_date"]>=midpoint]["quantity"].sum()); trend="INCREASING" if second>first*1.15 else "DECREASING" if second<first*.85 else "STABLE"; horizon=round(stock.get(str(pid),0)/avg,1) if avg>0 else None; risk="CRITICAL" if horizon is not None and horizon<3 else "HIGH" if horizon is not None and horizon<7 else "MEDIUM" if horizon is not None and horizon<14 else "LOW"
            forecasts.append(DemandForecast(product_id=str(pid),product_name=str(name),average_daily_demand=round(avg,2),demand_trend=trend,estimated_days_until_stockout=horizon,risk_level=risk))
        high=[x.product_id for x in forecasts if x.risk_level in {"CRITICAL","HIGH"}]
        return DemandOutput(forecasts=forecasts,high_risk_products=high,key_findings=[f"{len(high)} products may stock out within seven days.","Trend compares demand in the first and second halves of the observed window."],limitations=["This is a deterministic workshop estimate, not a production ML forecast.","Open orders are used as a proxy for demand."],confidence_score=.82)
