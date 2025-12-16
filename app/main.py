"""main module"""

import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import uvicorn

from app.system.utils.logger import register_http_logging
from app.system.model.model_loader import load_model
from app.interface.routes import router
from app.system.utils.logger import logger



# helper funciton to load model on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # model
    # Run the blocking load_model in a separate thread so the event loop is not blocked
    await asyncio.to_thread(load_model)
    logger.info('model loaded successfully')
    yield


# fastapi object
app = FastAPI(lifespan=lifespan)

register_http_logging(app)
app.include_router(router, prefix="/v1")



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8501)
