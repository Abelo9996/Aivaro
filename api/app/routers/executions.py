from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Execution, Workflow, User
from app.schemas import ExecutionCreate, ExecutionResponse
from app.routers.auth import get_current_user
from app.services.workflow_runner import WorkflowRunner

router = APIRouter()


@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    workflow_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Execution).join(Workflow).filter(Workflow.user_id == current_user.id)
    
    if workflow_id:
        query = query.filter(Execution.workflow_id == workflow_id)
    
    executions = query.order_by(Execution.started_at.desc()).all()
    return [ExecutionResponse.model_validate(e) for e in executions]


@router.post("/", response_model=ExecutionResponse)
async def create_execution(
    execution_data: ExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    workflow = db.query(Workflow).filter(
        Workflow.id == execution_data.workflow_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    execution = Execution(
        workflow_id=workflow.id,
        is_test=execution_data.is_test,
        trigger_data=execution_data.trigger_data
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Run the workflow
    runner = WorkflowRunner(db, execution.id)
    runner.run(execution_data.trigger_data)
    
    db.refresh(execution)
    return ExecutionResponse.model_validate(execution)


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    execution = db.query(Execution).join(Workflow).filter(
        Execution.id == execution_id,
        Workflow.user_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return ExecutionResponse.model_validate(execution)
