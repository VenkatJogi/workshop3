import pytest
from app.config import Settings
from app.models.workflow_state import SupplyChainWorkflowState
from app.services.event_service import EventService
from app.services.excel_service import excel_service
from app.services.gemini_service import GeminiService

@pytest.fixture
def services():
    return GeminiService(Settings()), EventService()

@pytest.fixture
def state():
    data, validations = {}, []
    for name in ("inventory", "orders", "suppliers"):
        data[name], validation = excel_service.read_sample(name)
        validations.append(validation.model_dump())
    return SupplyChainWorkflowState(
        workflow_id="test", business_objective="Prevent stockouts and protect priority orders.",
        inventory_data=data["inventory"], orders_data=data["orders"], suppliers_data=data["suppliers"],
        file_validations=validations, demo_conflict_mode=True, max_revisions=2,
    )
