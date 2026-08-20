from app.agents.base_agent import BaseAgent
from app.models.agent_outputs import DataIngestionOutput,FileValidation
class DataIngestionAgent(BaseAgent):
    name="data_ingestion"; description="Validates datasets and discovers their business relationships."; output_model=DataIngestionOutput
    async def generate(self,state,additional_context=None):
        validations=[FileValidation.model_validate(item) for item in state.file_validations]; issues=[issue for item in validations for issue in item.errors]
        return DataIngestionOutput(dataset_summary=f"Loaded {len(state.inventory_data)} inventory rows, {len(state.orders_data)} orders, and {len(state.suppliers_data)} supplier options.",relationships=["Inventory joins Orders through product_id.","Suppliers join Inventory through product_id."],important_columns=["current_stock","reorder_level","quantity","priority","lead_time_days","unit_price","reliability_score"],data_quality_issues=issues,potential_insights=["Compare available stock with pending demand.","Compare stockout horizon with supplier lead time.","Protect high-priority orders before lower-priority allocation."],validations=validations,confidence_score=.98 if not issues else .75)
