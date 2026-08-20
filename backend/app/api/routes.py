import asyncio
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.models.requests import SampleWorkflowRequest
from app.models.responses import CreateWorkflowResponse, HealthResponse
from app.models.workflow_state import SupplyChainWorkflowState
from app.services.excel_service import ExcelValidationError, excel_service
from app.services.workflow_service import workflow_store

router = APIRouter()
DATASETS = ("inventory", "orders", "suppliers")


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


def _start_workflow(request: Request, state: SupplyChainWorkflowState) -> None:
    task = asyncio.create_task(request.app.state.orchestrator.execute(state))
    request.app.state.tasks.add(task)
    task.add_done_callback(request.app.state.tasks.discard)


async def _state_from_uploads(request, objective, demo, inventory, orders, suppliers):
    uploads = {"inventory": inventory, "orders": orders, "suppliers": suppliers}
    if inventory is None or orders is None:
        raise HTTPException(422, "Inventory and orders Excel files are required. Supplier data is optional.")
    records = {name: [] for name in DATASETS}
    validations = []
    try:
        for dataset, upload in uploads.items():
            if upload is None:
                continue
            rows, validation = await excel_service.read_upload(upload, dataset)
            records[dataset] = rows
            validations.append(validation)
    except ExcelValidationError as exc:
        raise HTTPException(422, str(exc)) from exc
    invalid = [item for item in validations if item.status == "INVALID"]
    if invalid:
        raise HTTPException(422, {"message": "Excel validation failed", "files": [item.model_dump() for item in invalid]})
    return SupplyChainWorkflowState(
        workflow_id=str(uuid4()), business_objective=objective.strip(),
        inventory_data=records["inventory"], orders_data=records["orders"], suppliers_data=records["suppliers"],
        file_validations=[item.model_dump() for item in validations], demo_conflict_mode=demo,
        max_revisions=request.app.state.settings.max_revisions,
    )


@router.post("/api/workflows", response_model=CreateWorkflowResponse, status_code=202)
async def create_workflow(
    request: Request, business_objective: str = Form(...), demo_conflict_mode: bool = Form(False),
    inventory: UploadFile | None = File(None), orders: UploadFile | None = File(None),
    suppliers: UploadFile | None = File(None),
):
    settings = request.app.state.settings
    if not demo_conflict_mode and (not settings.gemini_api_key or not settings.gemini_model):
        raise HTTPException(503, "Live Gemini mode requires GEMINI_API_KEY and GEMINI_MODEL in backend/.env.")
    state = await _state_from_uploads(request, business_objective, demo_conflict_mode, inventory, orders, suppliers)
    await workflow_store.create(state)
    _start_workflow(request, state)
    return CreateWorkflowResponse(workflow_id=state.workflow_id)


@router.post("/api/workflows/sample", response_model=CreateWorkflowResponse, status_code=202)
async def create_sample_workflow(payload: SampleWorkflowRequest, request: Request):
    settings = request.app.state.settings
    if not payload.demo_conflict_mode and (not settings.gemini_api_key or not settings.gemini_model):
        raise HTTPException(503, "Live Gemini mode requires GEMINI_API_KEY and GEMINI_MODEL in backend/.env.")
    records, validations = {}, []
    try:
        for dataset in DATASETS:
            rows, validation = excel_service.read_sample(dataset)
            records[dataset] = rows
            validations.append(validation)
    except ExcelValidationError as exc:
        raise HTTPException(500, f"Bundled sample data is unavailable: {exc}") from exc
    state = SupplyChainWorkflowState(
        workflow_id=str(uuid4()), business_objective=payload.business_objective,
        inventory_data=records["inventory"], orders_data=records["orders"], suppliers_data=records["suppliers"],
        file_validations=[item.model_dump() for item in validations], demo_conflict_mode=payload.demo_conflict_mode,
        max_revisions=request.app.state.settings.max_revisions,
    )
    await workflow_store.create(state)
    _start_workflow(request, state)
    return CreateWorkflowResponse(workflow_id=state.workflow_id)


def require_state(workflow_id: str) -> SupplyChainWorkflowState:
    state = workflow_store.get(workflow_id)
    if not state:
        raise HTTPException(404, "Workflow not found")
    return state


@router.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    state = require_state(workflow_id)
    return {
        "workflow_id": state.workflow_id, "business_objective": state.business_objective,
        "status": state.workflow_status, "revision_count": state.revision_count,
        "selected_agents": state.selected_agents, "agent_executions": state.agent_executions,
        "events": state.execution_log, "file_validations": state.file_validations,
        "data_summary": state.data_summary, "plan": state.plan, "critic_review": state.critic_review,
        "revision_history": state.revision_history, "unresolved_issues": state.unresolved_issues,
    }


@router.get("/api/workflows/{workflow_id}/agents")
async def get_agents(workflow_id: str):
    state = require_state(workflow_id)
    outputs = {
        "data_ingestion": state.data_summary, "planner": state.plan,
        "inventory": state.inventory_analysis, "orders": state.orders_analysis,
        "demand": state.demand_analysis, "supplier": state.supplier_analysis,
        "cost_impact": state.cost_analysis, "decision": state.proposed_decision,
        "critic": state.critic_review, "action_planner": state.action_plan,
    }
    return {name: {"execution": state.agent_executions.get(name), "output": output,
                   "revisions": [item for item in state.revision_history if item.agent_name == name]}
            for name, output in outputs.items()}


@router.get("/api/workflows/{workflow_id}/result")
async def get_result(workflow_id: str):
    state = require_state(workflow_id)
    if state.workflow_status not in {"COMPLETED", "HUMAN_REVIEW_REQUIRED"}:
        raise HTTPException(409, "Workflow has not produced a final result")
    return {"workflow_id": workflow_id, "status": state.workflow_status, "decision": state.proposed_decision,
            "critic_review": state.critic_review, "action_plan": state.action_plan,
            "revision_count": state.revision_count, "unresolved_issues": state.unresolved_issues}


@router.get("/api/sample-data")
async def sample_data_manifest():
    return {"files": [{"dataset": name, "file_name": f"{name}.xlsx",
                       "download_url": f"/api/sample-data/{name}.xlsx"} for name in DATASETS]}


@router.get("/api/sample-data/{file_name}")
async def download_sample_data(file_name: str):
    if file_name not in {f"{name}.xlsx" for name in DATASETS}:
        raise HTTPException(404, "Sample file not found")
    path = excel_service.sample_dir / file_name
    if not path.is_file():
        raise HTTPException(404, "Sample file not found")
    return FileResponse(path, filename=file_name,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
