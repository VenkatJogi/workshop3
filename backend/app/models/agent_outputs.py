from typing import Literal
from pydantic import BaseModel, Field, field_validator

SPECIALISTS = {"inventory", "orders", "demand", "supplier", "cost_impact"}

class FileValidation(BaseModel):
    file_name: str; dataset: str; rows: int; columns: list[str]
    missing_values: dict[str, int]; duplicates: int
    status: Literal["VALID", "INVALID"]; errors: list[str] = Field(default_factory=list)

class DataIngestionOutput(BaseModel):
    dataset_summary: str; relationships: list[str]; important_columns: list[str]
    data_quality_issues: list[str]; potential_insights: list[str]
    validations: list[FileValidation]; confidence_score: float = Field(ge=0, le=1)

class PlannerOutput(BaseModel):
    business_problem: str; selected_agents: list[str]; decision_criteria: list[str]
    execution_strategy: Literal["PARALLEL"] = "PARALLEL"
    @field_validator("selected_agents")
    @classmethod
    def valid_agents(cls, value):
        invalid=set(value)-SPECIALISTS
        if invalid: raise ValueError(f"Unknown agents: {sorted(invalid)}")
        if not value: raise ValueError("At least one specialist is required")
        return list(dict.fromkeys(value))

class InventoryAlert(BaseModel):
    product_id: str; product_name: str; current_stock: float; reorder_level: float
    status: Literal["CRITICAL", "LOW", "HEALTHY", "OVERSTOCKED"]; issue: str
class InventoryOutput(BaseModel):
    total_products: int; critical_products: list[InventoryAlert]; low_stock_products: list[InventoryAlert]
    healthy_products: int; overstocked_products: list[InventoryAlert]
    key_findings: list[str]; confidence_score: float = Field(ge=0, le=1)

class OrderRisk(BaseModel):
    order_id: str; product_id: str; product_name: str; quantity: float; priority: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]; reason: str
class OrdersOutput(BaseModel):
    total_pending_orders: int; high_priority_orders: int; orders_at_risk: list[OrderRisk]
    product_demand_summary: list[dict]; key_findings: list[str]; confidence_score: float = Field(ge=0, le=1)

class DemandForecast(BaseModel):
    product_id: str; product_name: str; average_daily_demand: float
    demand_trend: Literal["DECREASING", "STABLE", "INCREASING"]
    estimated_days_until_stockout: float | None; risk_level: str
class DemandOutput(BaseModel):
    forecasts: list[DemandForecast]; high_risk_products: list[str]; key_findings: list[str]
    limitations: list[str]; confidence_score: float = Field(ge=0, le=1)

class SupplierOption(BaseModel):
    supplier_id: str; supplier_name: str; product_id: str; product_name: str
    unit_price: float; minimum_order_quantity: float; lead_time_days: float
    reliability_score: float; supplier_type: str; suitability: str
class SupplierOutput(BaseModel):
    supplier_recommendations: list[SupplierOption]; fast_delivery_options: list[SupplierOption]
    cost_effective_options: list[SupplierOption]; supplier_risks: list[str]
    key_findings: list[str]; confidence_score: float = Field(ge=0, le=1)

class ProductCostComparison(BaseModel):
    product_id: str; regular_supplier: str | None; regular_unit_price: float | None
    emergency_supplier: str | None; emergency_unit_price: float | None; premium_percentage: float | None
class CostImpactOutput(BaseModel):
    estimated_regular_cost: float | None; estimated_emergency_cost: float | None; additional_cost: float | None
    product_comparisons: list[ProductCostComparison]; cost_drivers: list[str]; potential_savings: list[str]
    tradeoffs: list[str]; recommendation: str; confidence_score: float = Field(ge=0, le=1)

class ProductDecision(BaseModel):
    product_id: str; product_name: str; priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    recommended_action: str; reasoning: str; supporting_evidence: list[str]
    risks: list[str]; assumptions: list[str]; estimated_business_impact: str
class DecisionOutput(BaseModel):
    executive_summary: str; product_decisions: list[ProductDecision]; overall_strategy: str
    key_tradeoffs: list[str]; unresolved_questions: list[str]; confidence_score: float = Field(ge=0, le=1)

class RevisionRequest(BaseModel):
    target_agent: str; reason: str; required_context: str
class CriticOutput(BaseModel):
    decision: Literal["APPROVE", "REVISE", "RESEARCH_MORE"]
    overall_confidence: float = Field(ge=0, le=1); strengths: list[str]; conflicts: list[str]
    unsupported_assumptions: list[str]; missing_information: list[str]
    revision_requests: list[RevisionRequest]; reasoning: str

class ActionItem(BaseModel):
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    action: str; owner: str | None; timeline: str; expected_outcome: str
class ActionPlanOutput(BaseModel):
    immediate_actions: list[ActionItem]; short_term_actions: list[ActionItem]
    monitoring_actions: list[ActionItem]; business_summary: str
