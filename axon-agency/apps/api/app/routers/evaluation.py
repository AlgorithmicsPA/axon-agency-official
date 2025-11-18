"""Evaluation endpoints for agent testing."""

import uuid
import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlmodel import Session, select
from loguru import logger

from app.core.database import get_session
from app.core.security import get_current_user
from app.models import User
from app.models.rag import (
    EvalDataset, EvalItem, EvalRun, EvalMetric,
    EvalRunStatus
)
from app.services.embeddings import embedding_service


router = APIRouter()


class DatasetCreateResponse(BaseModel):
    dataset_id: str
    item_count: int


class EvalRunRequest(BaseModel):
    dataset_id: str
    agent_id: str


class EvalRunResponse(BaseModel):
    run_id: str
    metrics: dict


class EvalMetricsResponse(BaseModel):
    exact_match: float
    semantic_similarity: float
    average_latency_ms: int
    total_items: int


@router.post("/datasets/create", response_model=DatasetCreateResponse)
async def create_dataset(
    file: UploadFile = File(...),
    name: str = "Evaluation Dataset",
    description: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create an evaluation dataset from CSV or JSON."""
    content = await file.read()
    
    try:
        if file.filename.endswith('.json'):
            data = json.loads(content)
        elif file.filename.endswith('.csv'):
            import csv
            import io
            reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
            data = list(reader)
        else:
            raise HTTPException(status_code=400, detail="Only JSON and CSV files are supported")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")
    
    dataset_id = f"dataset_{uuid.uuid4().hex[:12]}"
    
    dataset = EvalDataset(
        dataset_id=dataset_id,
        name=name,
        description=description,
        created_by=current_user.username
    )
    
    session.add(dataset)
    session.commit()
    session.refresh(dataset)
    
    items = []
    for row in data:
        question = row.get('question') or row.get('q') or row.get('input')
        expected = row.get('answer') or row.get('expected') or row.get('output')
        context = row.get('context')
        
        if not question or not expected:
            continue
        
        item = EvalItem(
            dataset_id=dataset.id,
            question=question,
            expected_answer=expected,
            context=context
        )
        session.add(item)
        items.append(item)
    
    session.commit()
    
    dataset.item_count = len(items)
    session.commit()
    
    logger.info(f"Created dataset {dataset_id} with {len(items)} items")
    
    return DatasetCreateResponse(
        dataset_id=dataset_id,
        item_count=len(items)
    )


async def process_eval_run(run_id: str, dataset_id: int, agent_id: str):
    """Background task to process evaluation run."""
    from app.core.database import Session as DBSession, engine
    
    session = DBSession(engine)
    
    try:
        stmt = select(EvalRun).where(EvalRun.run_id == run_id)
        run = session.exec(stmt).first()
        
        if not run:
            return
        
        run.status = EvalRunStatus.RUNNING
        run.started_at = datetime.utcnow()
        session.commit()
        
        stmt = select(EvalItem).where(EvalItem.dataset_id == dataset_id)
        items = session.exec(stmt).all()
        
        run.total_items = len(items)
        session.commit()
        
        for item in items:
            start_time = datetime.utcnow()
            
            actual_answer = f"Mock answer for: {item.question[:50]}"
            
            end_time = datetime.utcnow()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)
            
            exact_match = 1.0 if actual_answer.lower() == item.expected_answer.lower() else 0.0
            
            question_emb = await embedding_service.embed_text(item.question)
            expected_emb = await embedding_service.embed_text(item.expected_answer)
            actual_emb = await embedding_service.embed_text(actual_answer)
            
            semantic_similarity = embedding_service.cosine_similarity(expected_emb, actual_emb)
            
            metric = EvalMetric(
                run_id=run.id,
                item_id=item.id,
                exact_match=exact_match,
                semantic_similarity=semantic_similarity,
                latency_ms=latency_ms,
                actual_answer=actual_answer
            )
            session.add(metric)
            
            run.processed_items += 1
            run.progress = (run.processed_items / run.total_items) * 100
            session.commit()
        
        run.status = EvalRunStatus.COMPLETED
        run.completed_at = datetime.utcnow()
        session.commit()
        
        logger.info(f"Evaluation run {run_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Evaluation run {run_id} failed: {e}")
        
        if run:
            run.status = EvalRunStatus.FAILED
            session.commit()
    
    finally:
        session.close()


@router.post("/run", response_model=EvalRunResponse)
async def run_evaluation(
    request: EvalRunRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Run an evaluation on a dataset."""
    stmt = select(EvalDataset).where(EvalDataset.dataset_id == request.dataset_id)
    dataset = session.exec(stmt).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    
    run = EvalRun(
        run_id=run_id,
        dataset_id=dataset.id,
        agent_id=request.agent_id,
        status=EvalRunStatus.PENDING
    )
    
    session.add(run)
    session.commit()
    
    background_tasks.add_task(process_eval_run, run_id, dataset.id, request.agent_id)
    
    return EvalRunResponse(
        run_id=run_id,
        metrics={"status": "processing"}
    )


@router.get("/run/{run_id}", response_model=EvalMetricsResponse)
async def get_eval_run(
    run_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get evaluation run results."""
    stmt = select(EvalRun).where(EvalRun.run_id == run_id)
    run = session.exec(stmt).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    
    stmt = select(EvalMetric).where(EvalMetric.run_id == run.id)
    metrics = session.exec(stmt).all()
    
    if not metrics:
        return EvalMetricsResponse(
            exact_match=0.0,
            semantic_similarity=0.0,
            average_latency_ms=0,
            total_items=0
        )
    
    avg_exact = sum(m.exact_match for m in metrics) / len(metrics)
    avg_semantic = sum(m.semantic_similarity for m in metrics) / len(metrics)
    avg_latency = sum(m.latency_ms for m in metrics) // len(metrics)
    
    return EvalMetricsResponse(
        exact_match=avg_exact,
        semantic_similarity=avg_semantic,
        average_latency_ms=avg_latency,
        total_items=len(metrics)
    )


@router.get("/datasets/list")
async def list_datasets(
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List evaluation datasets."""
    stmt = select(EvalDataset).order_by(EvalDataset.created_at.desc()).limit(limit)
    datasets = session.exec(stmt).all()
    
    return {
        "items": [
            {
                "dataset_id": d.dataset_id,
                "name": d.name,
                "item_count": d.item_count,
                "created_at": d.created_at.isoformat()
            }
            for d in datasets
        ]
    }
