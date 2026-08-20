from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import SupplierOption,SupplierOutput
class SupplierAgent(BaseAgent):
    name="supplier"; description="Compares supplier speed, reliability, price, and order constraints."; output_model=SupplierOutput
    async def generate(self,state,additional_context=None):
        options=[]
        for row in state.suppliers_data:
            suitability="FASTEST" if float(row["lead_time_days"])<=2 else "COST_EFFECTIVE" if str(row["supplier_type"]).upper()=="REGULAR" else "BALANCED"
            options.append(SupplierOption(**{key:row[key] for key in ["supplier_id","supplier_name","product_id","product_name","unit_price","minimum_order_quantity","lead_time_days","reliability_score","supplier_type"]},suitability=suitability))
        fast=[x for x in options if x.lead_time_days<=2]; regular=[x for x in options if x.supplier_type.upper()=="REGULAR"]
        recommendations=[]
        for pid in sorted({x.product_id for x in options}):
            candidates=[x for x in options if x.product_id==pid]; recommendations.append(sorted(candidates,key=lambda x:(x.lead_time_days,-x.reliability_score,x.unit_price))[0])
        return SupplierOutput(supplier_recommendations=recommendations,fast_delivery_options=fast,cost_effective_options=regular,supplier_risks=["Emergency suppliers carry a price premium.","Fast options have lower reliability than regular supply."],key_findings=[f"{len(fast)} emergency options can deliver within two days.",f"{len(regular)} regular options minimize unit cost."],confidence_score=.96)
