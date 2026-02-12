from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import json

from app.database import get_db
from app.models import Execution, ExecutionNode, Workflow, User
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


@router.post("/stream", response_class=StreamingResponse)
async def create_execution_stream(
    execution_data: ExecutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and run an execution with SSE streaming for progress updates."""
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
    
    execution_id = str(execution.id)
    total_nodes = len(workflow.nodes or [])
    
    async def generate_progress():
        # Send initial event with execution info
        yield f"data: {json.dumps({'type': 'start', 'execution_id': execution_id, 'total_steps': total_nodes, 'workflow_name': workflow.name})}\n\n"
        
        # Run workflow in background and poll for progress
        import threading
        
        def run_workflow():
            runner = WorkflowRunner(db, execution.id)
            runner.run(execution_data.trigger_data)
        
        thread = threading.Thread(target=run_workflow)
        thread.start()
        
        completed_nodes = set()
        last_status = None
        
        while thread.is_alive() or last_status not in ['completed', 'failed']:
            await asyncio.sleep(0.3)  # Poll every 300ms
            
            # Refresh execution and nodes
            db.refresh(execution)
            exec_nodes = db.query(ExecutionNode).filter(
                ExecutionNode.execution_id == execution.id
            ).all()
            
            # Send updates for newly completed nodes
            for node in exec_nodes:
                if node.id not in completed_nodes and node.status in ['completed', 'failed']:
                    completed_nodes.add(node.id)
                    progress = len(completed_nodes) / total_nodes if total_nodes > 0 else 1
                    yield f"data: {json.dumps({'type': 'step', 'node_id': node.node_id, 'node_label': node.node_label, 'status': node.status, 'completed': len(completed_nodes), 'total': total_nodes, 'progress': progress})}\n\n"
            
            last_status = execution.status
        
        # Wait for thread to finish
        thread.join()
        
        # Send final completion event
        db.refresh(execution)
        yield f"data: {json.dumps({'type': 'complete', 'execution_id': execution_id, 'status': execution.status})}\n\n"
    
    return StreamingResponse(
        generate_progress(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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
