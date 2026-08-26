import asyncio
import uuid
import signal
from typing import Optional
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.processing import ProcessingJob, JobStatus
from app.processing.queue import ProcessingQueue
from app.processing.orchestrator import ProcessingOrchestrator
from app.processing.stages.ocr import OCRStage
from app.processing.stages.development import DevelopmentValidationStage
from app.processing.stages.extraction_stage import ExtractionStage
from app.core.logging import logger

class ProcessingWorker:
    def __init__(self, worker_id: Optional[str] = None):
        self.worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self.is_running = False
        
        # The authoritative pipeline stages
        from app.services.ocr.tesseract_adapter import TesseractAdapter
        tesseract = TesseractAdapter()
        stages = [
            OCRStage(ocr_provider=tesseract),
            ExtractionStage()
        ]
        
        self.orchestrator = ProcessingOrchestrator(stages=stages)

    async def _claim_job(self, job_id_str: str) -> Optional[ProcessingJob]:
        """
        Attempts to atomically claim a job. 
        Requires the job to be in QUEUED status.
        Transitions to PROCESSING if successful.
        """
        async with AsyncSessionLocal() as session:
            # We use select ... for update to prevent concurrent worker claims on PostgreSQL
            stmt = select(ProcessingJob).where(
                ProcessingJob.id == job_id_str,
                ProcessingJob.status == JobStatus.QUEUED
            ).with_for_update(skip_locked=True)
            
            result = await session.execute(stmt)
            job = result.scalar_one_or_none()
            
            if not job:
                # Job not found or not in QUEUED state or locked by another worker
                return None
                
            # Claim the job
            job.status = JobStatus.PROCESSING
            job.worker_id = self.worker_id
            
            await session.commit()
            
            # Keep the job instance fresh for the orchestration pipeline
            await session.refresh(job)
            return job

    async def start(self):
        self.is_running = True
        logger.info(f"Worker {self.worker_id} started. Listening for jobs...")
        
        while self.is_running:
            try:
                # Blocking pop from Redis with a short timeout
                job_id = await ProcessingQueue.dequeue_job(timeout=2)
                
                if job_id:
                    logger.info(f"Worker {self.worker_id} dequeued job: {job_id}")
                    
                    job = await self._claim_job(job_id)
                    if job:
                        # Proceed with orchestration
                        async with AsyncSessionLocal() as session:
                            session.add(job)
                            await self.orchestrator.run_pipeline(session, job)
                            
                            # If job was marked for retry (QUEUED), re-enqueue it immediately
                            if job.status == JobStatus.QUEUED:
                                await ProcessingQueue.enqueue_job(str(job.id))
                    else:
                        logger.warning(f"Worker {self.worker_id} failed to claim job {job_id}. Skipping.")
                        
            except asyncio.CancelledError:
                logger.info("Worker cancelled.")
                break
            except Exception as e:
                logger.error(f"Worker {self.worker_id} encountered an error: {e}")
                await asyncio.sleep(5) # Prevent tight spin on persistent errors

    def stop(self):
        logger.info(f"Worker {self.worker_id} stopping...")
        self.is_running = False

