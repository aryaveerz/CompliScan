"""
CompliScan LM — Standalone Background Worker Process Entry Point.
Polls and processes queued AnalysisJobs (Image Quality, Perception/OCR, Structured Extraction).
"""

import asyncio
import logging
import signal
import sys
from backend.app.core.config import settings
from backend.app.db.session import AsyncSessionLocal, async_engine
from backend.app.services.analysis_job_service import AnalysisJobService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("compliscan.worker")


async def run_worker():
    worker_id = f"standalone-worker-{asyncio.get_event_loop()._asyncgen_finalizers}"
    logger.info(f"Starting CompliScan standalone background worker (ID: {worker_id})...")
    logger.info(f"Poll interval: {settings.WORKER_POLL_INTERVAL_SECONDS}s, Max attempts: {settings.WORKER_MAX_JOB_ATTEMPTS}")

    running = True

    def _shutdown_handler():
        nonlocal running
        logger.info("Shutdown signal received. Stopping worker loop...")
        running = False

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown_handler)
        except NotImplementedError:
            # Signal handlers not implemented on Windows event loop for non-main thread
            pass

    try:
        while running:
            try:
                async with AsyncSessionLocal() as db:
                    processed = await AnalysisJobService.run_pending_jobs_inline(
                        db, worker_id=worker_id
                    )
                    if processed > 0:
                        logger.info(f"Processed {processed} job(s) in batch.")
            except Exception as e:
                logger.error(f"Error during job processing: {e}", exc_info=True)

            await asyncio.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)
    finally:
        logger.info("Disposing database connection pool...")
        await async_engine.dispose()
        logger.info("Worker process stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker terminated by user.")
        sys.exit(0)
