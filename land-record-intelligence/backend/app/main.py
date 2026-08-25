import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import APIException, api_exception_handler, global_exception_handler
from app.db.redis_client import redis_client
from app.api.v1.router import router as v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Bhu-Lekh API...")
    await redis_client.connect()
    yield
    logger.info("Shutting down Bhu-Lekh API...")
    await redis_client.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Exception Handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Health endpoint at root
@app.get("/health", tags=["System"])
async def root_health_check():
    # Simple ping for ALB/K8s/Docker Healthcheck that doesn't hit DB/Cache
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

# API v1 Router
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])
