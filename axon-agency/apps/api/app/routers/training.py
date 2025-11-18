"""Agent Training endpoints."""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlmodel import Session, select
from loguru import logger

from app.core.database import get_session
from app.core.security import get_current_user
from app.models import User
from app.models.rag import TrainingJob, TrainingJobStatus, RagChunk
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store


router = APIRouter()


class TrainingStartRequest(BaseModel):
    agent_id: str
    corpus_id: str
    params: dict = {}


class TrainingStartResponse(BaseModel):
    job_id: str
    eta: Optional[int] = None


class TrainingStatusResponse(BaseModel):
    status: str
    progress: float
    total_chunks: int
    processed_chunks: int
    error_message: Optional[str] = None


async def process_training_job(job_id: str):
    """Background task to process training job."""
    from app.core.database import Session as DBSession, engine
    
    session = DBSession(engine)
    
    try:
        stmt = select(TrainingJob).where(TrainingJob.job_id == job_id)
        job = session.exec(stmt).first()
        
        if not job:
            return
        
        job.status = TrainingJobStatus.RUNNING
        job.started_at = datetime.utcnow()
        session.commit()
        
        stmt = select(RagChunk).where(RagChunk.corpus_id == job.corpus_id)
        chunks = session.exec(stmt).all()
        
        job.total_chunks = len(chunks)
        session.commit()
        
        chunk_texts = [chunk.text for chunk in chunks]
        chunk_ids = [chunk.id for chunk in chunks]
        
        if chunk_texts:
            embeddings = await embedding_service.embed_batch(chunk_texts, batch_size=50)
            
            vector_store.add_vectors(job.corpus_id, embeddings, chunk_ids)
            
            job.processed_chunks = len(chunks)
            job.progress = 100.0
            job.status = TrainingJobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
        else:
            job.status = TrainingJobStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.utcnow()
        
        session.commit()
        logger.info(f"Training job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Training job {job_id} failed: {e}")
        
        if job:
            job.status = TrainingJobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            session.commit()
    
    finally:
        session.close()


@router.post("/start", response_model=TrainingStartResponse)
async def start_training(
    request: TrainingStartRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Start a training job for an agent."""
    job_id = f"train_{uuid.uuid4().hex[:12]}"
    
    job = TrainingJob(
        job_id=job_id,
        agent_id=request.agent_id,
        corpus_id=request.corpus_id,
        params=request.params,
        status=TrainingJobStatus.PENDING
    )
    
    session.add(job)
    session.commit()
    
    background_tasks.add_task(process_training_job, job_id)
    
    logger.info(f"Started training job {job_id} for agent {request.agent_id}")
    
    return TrainingStartResponse(
        job_id=job_id,
        eta=120
    )


@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get status of a training job."""
    stmt = select(TrainingJob).where(TrainingJob.job_id == job_id)
    job = session.exec(stmt).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return TrainingStatusResponse(
        status=job.status.value,
        progress=job.progress,
        total_chunks=job.total_chunks,
        processed_chunks=job.processed_chunks,
        error_message=job.error_message
    )


@router.get("/list")
async def list_training_jobs(
    agent_id: Optional[str] = None,
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List training jobs."""
    stmt = select(TrainingJob)
    
    if agent_id:
        stmt = stmt.where(TrainingJob.agent_id == agent_id)
    
    stmt = stmt.order_by(TrainingJob.created_at.desc()).limit(limit)
    
    jobs = session.exec(stmt).all()
    
    return {
        "items": [
            {
                "job_id": j.job_id,
                "agent_id": j.agent_id,
                "corpus_id": j.corpus_id,
                "status": j.status.value,
                "progress": j.progress,
                "created_at": j.created_at.isoformat()
            }
            for j in jobs
        ]
    }
