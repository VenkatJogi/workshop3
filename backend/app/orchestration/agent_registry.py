from app.agents.inventory_agent import InventoryAgent
from app.agents.orders_agent import OrdersAgent
from app.agents.demand_agent import DemandAgent
from app.agents.supplier_agent import SupplierAgent
from app.agents.cost_impact_agent import CostImpactAgent
AGENT_REGISTRY={"inventory":InventoryAgent,"orders":OrdersAgent,"demand":DemandAgent,"supplier":SupplierAgent,"cost_impact":CostImpactAgent}
RESULT_FIELDS={"inventory":"inventory_analysis","orders":"orders_analysis","demand":"demand_analysis","supplier":"supplier_analysis","cost_impact":"cost_analysis"}
def get_agent_class(name):
    if name not in AGENT_REGISTRY: raise ValueError(f"Unknown agent target: {name}")
    return AGENT_REGISTRY[name]
