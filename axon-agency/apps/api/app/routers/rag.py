"""RAG (Retrieval Augmented Generation) endpoints - Full Implementation."""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from sqlmodel import Session, select
from loguru import logger

from app.core.database import get_session
from app.core.security import get_current_user
from app.models import User
from app.models.rag import RagSource, RagChunk, SourceType
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.services.document_processor import document_processor


router = APIRouter()


MAX_UPLOAD_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt", ".zip"}
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "./storage"))


class UploadResponse(BaseModel):
    corpus_id: str
    items: int
    chunks: int
    source_id: int


class URLUploadRequest(BaseModel):
    url: HttpUrl
    corpus_id: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None
    corpus_id: Optional[str] = None
    k: int = 10


class QueryAnswer(BaseModel):
    text: str
    score: float
    refs: List[dict]


class QueryResponse(BaseModel):
    answers: List[QueryAnswer]
    used_model: str
    topk: int


@router.post("/sources/upload", response_model=UploadResponse)
async def upload_source(
    file: UploadFile = File(...),
    corpus_id: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Upload and index a document (PDF, Markdown, Text, ZIP)."""
    if not corpus_id:
        corpus_id = f"corpus_{uuid.uuid4().hex[:12]}"
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    upload_dir = STORAGE_ROOT / "uploads" / corpus_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    file_size = 0
    with open(file_path, 'wb') as f:
        while chunk := await file.read(1024 * 1024):
            file_size += len(chunk)
            if file_size > MAX_UPLOAD_SIZE:
                file_path.unlink()
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {MAX_UPLOAD_SIZE // 1024 // 1024}MB"
                )
            f.write(chunk)
    
    source_type = SourceType.PDF if file_ext == ".pdf" else SourceType.MARKDOWN if file_ext == ".md" else SourceType.TEXT
    
    source = RagSource(
        corpus_id=corpus_id,
        source_type=source_type,
        name=file.filename,
        file_path=str(file_path),
        file_size=file_size
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    
    if file_ext == ".pdf":
        text_chunks = await document_processor.process_pdf(file_path)
    elif file_ext == ".md":
        text_chunks = await document_processor.process_markdown(file_path)
    else:
        text_chunks = await document_processor.process_text(file_path)
    
    chunk_objects = []
    chunk_texts = []
    chunk_ids = []
    
    for idx, (text, meta) in enumerate(text_chunks):
        token_count = document_processor.estimate_tokens(text)
        page_num = meta.get("page")
        
        chunk = RagChunk(
            source_id=source.id,
            corpus_id=corpus_id,
            text=text,
            chunk_index=idx,
            token_count=token_count,
            page_number=page_num,
            meta=meta
        )
        session.add(chunk)
        chunk_objects.append(chunk)
        chunk_texts.append(text)
    
    session.commit()
    
    for chunk in chunk_objects:
        session.refresh(chunk)
        chunk_ids.append(chunk.id)
    
    if chunk_texts:
        embeddings = await embedding_service.embed_batch(chunk_texts)
        vector_store.add_vectors(corpus_id, embeddings, chunk_ids)
        
        for chunk, embedding in zip(chunk_objects, embeddings):
            chunk.embedding = str(embedding[:10])
        session.commit()
    
    source.chunk_count = len(chunk_texts)
    session.commit()
    
    logger.info(f"Uploaded {file.filename}: {len(chunk_texts)} chunks to corpus {corpus_id}")
    
    return UploadResponse(
        corpus_id=corpus_id,
        items=1,
        chunks=len(chunk_texts),
        source_id=source.id
    )


@router.post("/sources/url", response_model=UploadResponse)
async def upload_url(
    request: URLUploadRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Scrape and index content from a URL."""
    corpus_id = request.corpus_id or f"corpus_{uuid.uuid4().hex[:12]}"
    url_str = str(request.url)
    
    source = RagSource(
        corpus_id=corpus_id,
        source_type=SourceType.URL,
        name=url_str,
        url=url_str
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    
    text_chunks = await document_processor.process_url(url_str)
    
    if not text_chunks:
        raise HTTPException(status_code=400, detail="Failed to extract content from URL")
    
    chunk_objects = []
    chunk_texts = []
    chunk_ids = []
    
    for idx, (text, meta) in enumerate(text_chunks):
        token_count = document_processor.estimate_tokens(text)
        
        chunk = RagChunk(
            source_id=source.id,
            corpus_id=corpus_id,
            text=text,
            chunk_index=idx,
            token_count=token_count,
            meta=meta
        )
        session.add(chunk)
        chunk_objects.append(chunk)
        chunk_texts.append(text)
    
    session.commit()
    
    for chunk in chunk_objects:
        session.refresh(chunk)
        chunk_ids.append(chunk.id)
    
    if chunk_texts:
        embeddings = await embedding_service.embed_batch(chunk_texts)
        vector_store.add_vectors(corpus_id, embeddings, chunk_ids)
        
        for chunk, embedding in zip(chunk_objects, embeddings):
            chunk.embedding = str(embedding[:10])
        session.commit()
    
    source.chunk_count = len(chunk_texts)
    session.commit()
    
    logger.info(f"Indexed URL {url_str}: {len(chunk_texts)} chunks to corpus {corpus_id}")
    
    return UploadResponse(
        corpus_id=corpus_id,
        items=1,
        chunks=len(chunk_texts),
        source_id=source.id
    )


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Query the RAG system with semantic search."""
    corpus_id = request.corpus_id or "default"
    
    query_embedding = await embedding_service.embed_text(request.query)
    
    results = vector_store.search(corpus_id, query_embedding, k=request.k)
    
    if not results:
        return QueryResponse(
            answers=[],
            used_model=embedding_service.model if embedding_service.use_openai else "local",
            topk=0
        )
    
    chunk_ids = [chunk_id for chunk_id, _ in results]
    
    stmt = select(RagChunk).where(RagChunk.id.in_(chunk_ids))
    chunks = session.exec(stmt).all()
    
    chunk_dict = {chunk.id: chunk for chunk in chunks}
    
    answers = []
    for chunk_id, score in results:
        chunk = chunk_dict.get(chunk_id)
        if chunk:
            source_stmt = select(RagSource).where(RagSource.id == chunk.source_id)
            source = session.exec(source_stmt).first()
            
            refs = [{
                "source": source.name if source else "unknown",
                "loc": chunk.page_number or chunk.chunk_index,
                "url": source.url if source and source.url else None
            }]
            
            answers.append(QueryAnswer(
                text=chunk.text,
                score=score,
                refs=refs
            ))
    
    return QueryResponse(
        answers=answers,
        used_model=embedding_service.model if embedding_service.use_openai else "local",
        topk=len(answers)
    )


@router.get("/corpus/{corpus_id}/stats")
async def get_corpus_stats(
    corpus_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific corpus."""
    stmt = select(RagSource).where(RagSource.corpus_id == corpus_id)
    sources = session.exec(stmt).all()
    
    stmt = select(RagChunk).where(RagChunk.corpus_id == corpus_id)
    chunks = session.exec(stmt).all()
    
    vector_stats = vector_store.get_stats(corpus_id)
    
    return {
        "corpus_id": corpus_id,
        "sources": len(sources),
        "chunks": len(chunks),
        "total_tokens": sum(chunk.token_count for chunk in chunks),
        "vector_index": vector_stats
    }
