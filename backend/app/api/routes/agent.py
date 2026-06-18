from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import AgentRun
from app.schemas.agent import AgentRunCreate, AgentRunRead
from app.services.agent_runner import AgentRunner

router = APIRouter()


@router.post("/runs", response_model=AgentRunRead, status_code=201)
async def create_run(payload: AgentRunCreate, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        run, result = await AgentRunner().create_and_run(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _read(run, result)


@router.get("/runs/{run_id}", response_model=AgentRunRead)
async def get_run(run_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found.")
    result = await AgentRunner().get_result_for_run(db, run_id)
    return _read(run, result)


def _read(run: AgentRun, result) -> dict:
    return {
        "id": run.id,
        "product_id": run.product_id,
        "status": run.status,
        "progress": run.progress,
        "current_step": run.current_step,
        "input_snapshot": run.input_snapshot,
        "error_message": run.error_message,
        "result": result,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
    }
