from fastapi import Depends, FastAPI, Header, HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, get_engine, get_session
from .repository import ingest_message
from .schemas import IngestResult, MessageEventV1


app = FastAPI(title="Sera Message Intelligence", version="0.1.0", description="Local-first multi-IM message ingest and intelligence core.")


@app.on_event("startup")
def create_tables_for_p0() -> None:
    Base.metadata.create_all(bind=get_engine())


def require_ingest_key(x_smi_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().ingest_api_key
    if expected and x_smi_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid ingest api key")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/messages", response_model=IngestResult, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_ingest_key)])
def ingest(event: MessageEventV1, session: Session = Depends(get_session)) -> IngestResult:
    return ingest_message(session, event)
