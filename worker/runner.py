"""
CompliScan LM — Background Worker Runner.
Polls and processes durable analysis jobs from the database queue.
"""

import asyncio
import logging
import os
import signal
import socket
import sys
from typing import Optional

from backend.app.db.session import async_session_factory
from backend.app.services.analysis_job_service import AnalysisJobService
from backend.app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Worker] %(message)s",
)
logger = logging.getLogger("compliscan.worker")


class WorkerRunner:
    def __init__(self, worker_id: Optional[str] = None):
        hostname = socket.gethostname()
        pid = os.getpid()
        self.worker_id = worker_id or f"worker-{hostname}-{pid}"
        self.is_running = False

    async def process_one_job(self) -> bool:
        """
        Attempt to claim and process a single job.
        Returns True if a job was processed, False if queue was empty.
        """
        async with async_session_factory() as db:
            job = await AnalysisJobService.claim_next_job(
                db=db,
                worker_id=self.worker_id,
                lease_seconds=settings.WORKER_LEASE_SECONDS,
            )
            if not job:
                return False

            logger.info(
                f"Claimed job {job.id} (type: {job.job_type}, inspection: {job.inspection_id}, attempt: {job.attempts})"
            )

            try:
                await AnalysisJobService.execute_job(db=db, job=job)
                await db.commit()
                logger.info(f"Completed job {job.id} with status {job.status}")
            except Exception as e:
                await db.rollback()
                logger.error(f"Error processing job {job.id}: {str(e)}", exc_info=True)

            return True

    async def run_loop(
        self,
        poll_interval: Optional[float] = None,
        max_iterations: Optional[int] = None,
    ) -> None:
        """
        Continuous worker polling loop.
        """
        interval = poll_interval or settings.WORKER_POLL_INTERVAL_SECONDS
        self.is_running = True
        logger.info(f"Worker {self.worker_id} started (poll interval: {interval}s)")

        iterations = 0
        while self.is_running:
            if max_iterations is not None and iterations >= max_iterations:
                break

            try:
                processed = await self.process_one_job()
                iterations += 1
                if not processed:
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info("Worker received cancel signal. Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Unexpected worker loop exception: {str(e)}", exc_info=True)
                await asyncio.sleep(interval)

        logger.info(f"Worker {self.worker_id} stopped.")

    def stop(self) -> None:
        self.is_running = False


async def main():
    runner = WorkerRunner()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, runner.stop)
        except NotImplementedError:
            # Signal handlers not fully supported on Windows event loops
            pass

    await runner.run_loop()


if __name__ == "__main__":
    asyncio.run(main())
