import uuid
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select, col
from loguru import logger

from app.core.database import get_session, get_engine
from app.core.security import get_current_user
from app.models import User, ImprovementType, ImprovementJobStatus, ImprovementJob
from app.services.self_modification import self_modification_engine


router = APIRouter()


class CreateJobRequest(BaseModel):
    improvement_type: ImprovementType
    target_file: str
    title: str
    description: str
    rationale: Optional[str] = None
    priority: int = 5
    success_criteria: dict = {}


class JobResponse(BaseModel):
    id: int
    job_id: str
    improvement_type: ImprovementType
    target_file: str
    title: str
    description: str
    rationale: Optional[str]
    status: ImprovementJobStatus
    priority: int
    diff_preview: Optional[str]
    success_criteria: dict
    before_metrics: dict
    after_metrics: dict
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    worktree_path: Optional[str]
    meta: dict
    created_at: datetime
    updated_at: datetime


class ApproveJobRequest(BaseModel):
    approved_by: str


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[ImprovementJobStatus] = None,
    target_file: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(ImprovementJob)
    
    if status:
        query = query.where(ImprovementJob.status == status)
    if target_file:
        query = query.where(ImprovementJob.target_file == target_file)
    
    query = query.order_by(col(ImprovementJob.priority).desc(), col(ImprovementJob.created_at).desc())
    query = query.limit(limit).offset(offset)
    
    jobs = session.exec(query).all()
    
    count_query = select(ImprovementJob)
    if status:
        count_query = count_query.where(ImprovementJob.status == status)
    if target_file:
        count_query = count_query.where(ImprovementJob.target_file == target_file)
    
    total = len(session.exec(count_query).all())
    
    return JobListResponse(
        jobs=[JobResponse(**job.dict()) for job in jobs],
        total=total
    )


@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(
    request: CreateJobRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job_id = f"improve_{uuid.uuid4().hex[:12]}"
    
    job = ImprovementJob(
        job_id=job_id,
        improvement_type=request.improvement_type,
        target_file=request.target_file,
        title=request.title,
        description=request.description,
        rationale=request.rationale,
        priority=request.priority,
        success_criteria=request.success_criteria,
        status=ImprovementJobStatus.PENDING
    )
    
    session.add(job)
    session.commit()
    session.refresh(job)
    
    logger.info(f"Created improvement job {job_id} for {request.target_file}")
    
    return JobResponse(**job.dict())


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(**job.dict())


@router.patch("/jobs/{job_id}/approve", response_model=JobResponse)
async def approve_job(
    job_id: str,
    request: ApproveJobRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != ImprovementJobStatus.PENDING and job.status != ImprovementJobStatus.IN_REVIEW:
        raise HTTPException(status_code=400, detail=f"Cannot approve job with status {job.status}")
    
    job.status = ImprovementJobStatus.APPROVED
    job.approved_by = request.approved_by
    job.approved_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    
    session.add(job)
    session.commit()
    session.refresh(job)
    
    logger.info(f"Approved improvement job {job_id} by {request.approved_by}")
    
    return JobResponse(**job.dict())


@router.patch("/jobs/{job_id}/reject", response_model=JobResponse)
async def reject_job(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in [ImprovementJobStatus.PENDING, ImprovementJobStatus.IN_REVIEW]:
        raise HTTPException(status_code=400, detail=f"Cannot reject job with status {job.status}")
    
    job.status = ImprovementJobStatus.REJECTED
    job.updated_at = datetime.utcnow()
    
    session.add(job)
    session.commit()
    session.refresh(job)
    
    logger.info(f"Rejected improvement job {job_id}")
    
    return JobResponse(**job.dict())


@router.delete("/jobs/{job_id}", status_code=204)
async def cancel_job(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status in [ImprovementJobStatus.COMPLETED, ImprovementJobStatus.FAILED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status {job.status}")
    
    job.status = ImprovementJobStatus.CANCELLED
    job.updated_at = datetime.utcnow()
    
    session.add(job)
    session.commit()
    
    logger.info(f"Cancelled improvement job {job_id}")
    
    return None


async def run_job(job_id: str):
    """Background async job execution with proper event loop integration."""
    try:
        with Session(get_engine()) as bg_session:
            job = bg_session.exec(
                select(ImprovementJob).where(ImprovementJob.job_id == job_id)
            ).first()
            
            if not job:
                logger.error(f"Job {job_id} not found in background task")
                return
            
            result = await self_modification_engine.execute_improvement(job)
            
            job_update = bg_session.exec(
                select(ImprovementJob).where(ImprovementJob.job_id == job_id)
            ).first()
            
            if not job_update:
                logger.error(f"Job {job_id} disappeared during execution")
                return
            
            if result["status"] == "success":
                job_update.diff_preview = result.get("diff", "")
                job_update.after_metrics = result.get("after_metrics", {})
                job_update.worktree_path = result.get("temp_workspace")
                job_update.status = ImprovementJobStatus.COMPLETED
                job_update.completed_at = datetime.utcnow()
                logger.info(f"Successfully executed job {job_id} - changes applied directly to repo")
            else:
                job_update.status = ImprovementJobStatus.FAILED
                job_update.error_message = result.get("error", "Unknown error")
                logger.error(f"Job {job_id} failed: {job_update.error_message}")
            
            job_update.updated_at = datetime.utcnow()
            bg_session.add(job_update)
            bg_session.commit()
        
    except Exception as e:
        logger.error(f"Error in background execution: {e}")
        with Session(get_engine()) as bg_session:
            job_update = bg_session.exec(
                select(ImprovementJob).where(ImprovementJob.job_id == job_id)
            ).first()
            if job_update:
                job_update.status = ImprovementJobStatus.FAILED
                job_update.error_message = str(e)
                job_update.updated_at = datetime.utcnow()
                bg_session.add(job_update)
                bg_session.commit()


@router.post("/jobs/{job_id}/execute", response_model=JobResponse)
async def execute_job(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Execute an approved improvement job."""
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != ImprovementJobStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute job with status {job.status}. Must be APPROVED."
        )
    
    job.status = ImprovementJobStatus.RUNNING
    job.started_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    session.add(job)
    session.commit()
    session.refresh(job)
    
    asyncio.create_task(run_job(job_id))
    
    logger.info(f"Started execution of improvement job {job_id}")
    return JobResponse(**job.dict())


@router.post("/jobs/{job_id}/apply", response_model=JobResponse)
async def apply_job(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Mark improvement as applied (legacy endpoint - changes are now applied automatically during execution).
    This endpoint exists for API compatibility but changes are already in the repository.
    """
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != ImprovementJobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot apply job with status {job.status}. Must be COMPLETED."
        )
    
    job.meta = job.meta or {}
    job.meta["applied_at"] = datetime.utcnow().isoformat()
    job.meta["applied_by"] = current_user.username
    job.meta["note"] = "Changes were applied directly during execution"
    job.updated_at = datetime.utcnow()
    
    session.add(job)
    session.commit()
    session.refresh(job)
    
    logger.info(f"Marked improvement job {job_id} as applied (changes already in repo)")
    
    return JobResponse(**job.dict())


@router.delete("/jobs/{job_id}/cleanup", status_code=204)
async def cleanup_job(
    job_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Clean up temp workspace for a completed job (usually done automatically)."""
    job = session.exec(
        select(ImprovementJob).where(ImprovementJob.job_id == job_id)
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.worktree_path:
        await self_modification_engine.cleanup_workspace(job.worktree_path)
        job.worktree_path = None
        job.updated_at = datetime.utcnow()
        session.add(job)
        session.commit()
        logger.info(f"Cleaned up temp workspace for job {job_id}")
    
    return None
