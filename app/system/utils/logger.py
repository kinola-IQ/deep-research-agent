"""module to log system events"""
import logging
import time

# instantiating logger
logger = logging.getLogger('uvicorn.error')


# keep track of responsiveness across endpoints
def register_http_logging(app):
    """Processing time logger for HTTP requests and response status."""
    @app.middleware("http")
    async def log_process_time(request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as error:
            elapsed = time.perf_counter() - start
            # Log exception with traceback and request context
            logger.exception(f"{request.method} {request.url.path} failed in {elapsed:.3f}s")
            raise

        elapsed = time.perf_counter() - start
        status = getattr(response, "status_code", "?")
        logger.info(f"{request.method} {request.url.path} {status} completed in {elapsed:.3f}s")
        return response
