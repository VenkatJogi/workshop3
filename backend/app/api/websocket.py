from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.event_service import event_service
from app.services.workflow_service import workflow_store

router=APIRouter()


@router.websocket("/ws/workflows/{workflow_id}")
async def workflow_socket(websocket:WebSocket,workflow_id:str):
    state=workflow_store.get(workflow_id)
    if not state:
        await websocket.close(code=4404,reason="Workflow not found"); return
    await websocket.accept()
    for event in state.execution_log: await websocket.send_json(event.model_dump(mode="json"))
    if state.workflow_status in {"COMPLETED", "HUMAN_REVIEW_REQUIRED", "FAILED"}:
        await websocket.close(code=1000, reason="Workflow complete")
        return
    queue=event_service.subscribe(workflow_id)
    try:
        while True:
            event=await queue.get(); await websocket.send_json(event.model_dump(mode="json"))
            if event.event in {"workflow_completed", "human_review_required", "agent_failed"}: break
    except WebSocketDisconnect: pass
    finally: event_service.unsubscribe(workflow_id,queue)
