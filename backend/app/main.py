from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.config import get_settings
from app.orchestration.workflow import WorkflowOrchestrator
from app.services.event_service import event_service
from app.services.gemini_service import GeminiService
from app.utils.logger import configure_logging


@asynccontextmanager
async def lifespan(app:FastAPI):
    settings=get_settings(); configure_logging(settings.log_level)
    app.state.settings=settings; app.state.tasks=set(); app.state.orchestrator=WorkflowOrchestrator(GeminiService(settings),event_service)
    yield


app=FastAPI(title="SupplyChain AI Copilot",version="2.0.0",lifespan=lifespan)
settings=get_settings()
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_url],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(api_router); app.include_router(ws_router)
