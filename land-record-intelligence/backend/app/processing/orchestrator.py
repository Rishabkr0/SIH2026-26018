from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.models.processing import ProcessingJob, JobStatus
from app.processing.stages.base import ProcessingStage
from app.core.logging import logger

class ProcessingOrchestrator:
    """
    Manages the sequential execution of a list of ProcessingStages.
    """
    def __init__(self, stages: List[ProcessingStage]):
        self.stages = stages

    async def run_pipeline(self, session: AsyncSession, job: ProcessingJob) -> bool:
        """
        Executes the processing pipeline for a given job.
        Expects the job to already be in PROCESSING state and locked by the caller.
        
        Returns:
            bool: True if pipeline completed successfully, False otherwise.
        """
        if job.status != JobStatus.PROCESSING:
            logger.error(f"Job {job.id} cannot be run; status is {job.status}")
            return False

        logger.info(f"Starting pipeline execution for job {job.id} with {len(self.stages)} stages.")
        
        job.started_at = datetime.now(timezone.utc)
        job.error_message = None
        
        # We need the document
        from app.models.document import Document
        document = await session.get(Document, job.document_id)
        if not document:
            logger.error(f"Job {job.id} failed: Document not found")
            return False
        
        if not job.job_metadata:
            job.job_metadata = {}
            
        job.job_metadata["stages_executed"] = []

        try:
            for stage in self.stages:
                logger.info(f"Job {job.id}: Running stage '{stage.name}'")
                
                start_time = datetime.now(timezone.utc)
                
                # Execute stage
                stage_result = await stage.execute(session, job, document)
                
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                # Store stage metadata
                job.job_metadata[stage.name] = stage_result
                job.job_metadata["stages_executed"].append({
                    "name": stage.name,
                    "duration_seconds": duration,
                    "completed_at": end_time.isoformat()
                })
                
                logger.info(f"Job {job.id}: Stage '{stage.name}' completed in {duration:.2f}s")

            # Pipeline finished successfully
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            session.add(job)
            await session.commit()
            
            logger.info(f"Job {job.id} completed successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Job {job.id} failed during pipeline execution: {e}")
            await session.rollback() # Rollback any partial stage database changes
            
            # Re-fetch the job in a fresh state to mark as failed
            session.add(job)
            
            job.error_message = str(e)
            
            # Handle retry policy
            MAX_RETRIES = 3
            if job.retry_count < MAX_RETRIES:
                job.retry_count += 1
                job.status = JobStatus.QUEUED
                job.queued_at = datetime.now(timezone.utc)
                logger.info(f"Job {job.id} will be retried. Retry {job.retry_count}/{MAX_RETRIES}")
            else:
                job.status = JobStatus.FAILED
                job.failed_at = datetime.now(timezone.utc)
                logger.error(f"Job {job.id} exceeded max retries. Marking as FAILED.")
                
            session.add(job)
            await session.commit()
            return False
