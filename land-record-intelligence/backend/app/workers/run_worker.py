import asyncio
import signal
import sys
from app.core.logging import logger
from app.db.redis_client import redis_client
from app.processing.worker import ProcessingWorker

async def main():
    logger.info("Initializing worker environment...")
    
    # Initialize redis connection
    await redis_client.connect()
    
    worker = ProcessingWorker()
    
    def shutdown_handler(sig, frame):
        logger.info("Received shutdown signal. Stopping worker...")
        worker.stop()
        
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    try:
        await worker.start()
    finally:
        await redis_client.close()
        logger.info("Worker gracefully shutdown.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
