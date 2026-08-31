from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, get_engine, get_session
from .monitoring import collector_state_view
from .repository import ingest_message, list_collector_states, upsert_collector_heartbeat
from .schemas import CollectorHeartbeat, CollectorHeartbeatResult, CollectorStateView, IngestResult, MessageEventV1


app = FastAPI(title="Sera Message Intelligence", version="0.1.0", description="Local-first multi-IM message ingest and intelligence core.")


@app.on_event("startup")
def create_tables_for_p0() -> None:
    Base.metadata.create_all(bind=get_engine())


def require_ingest_key(x_smi_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().ingest_api_key
    if expected and x_smi_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/messages", response_model=IngestResult, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_ingest_key)])
def ingest(event: MessageEventV1, session: Session = Depends(get_session)) -> IngestResult:
    return ingest_message(session, event)


@app.post("/v1/collectors/heartbeat", response_model=CollectorHeartbeatResult, dependencies=[Depends(require_ingest_key)])
def collector_heartbeat(heartbeat: CollectorHeartbeat, session: Session = Depends(get_session)) -> CollectorHeartbeatResult:
    state = upsert_collector_heartbeat(session, heartbeat)
    return CollectorHeartbeatResult(collector_instance_id=state.collector_instance_id, status=state.status)


@app.get("/v1/collectors", response_model=list[CollectorStateView], dependencies=[Depends(require_ingest_key)])
def collectors(session: Session = Depends(get_session)) -> list[CollectorStateView]:
    settings=get_settings()
    return [collector_state_view(state, stale_seconds=settings.collector_stale_seconds) for state in list_collector_states(session)]
