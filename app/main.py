from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app import limiter
from .routers import auth_routes, entries

app = FastAPI(
    title="AquaLog API",
    description=(
        "Track maintenance tasks for home aquariums — feedings, water changes, "
        "filter cleans, and water-parameter checks. Data is stored in memory "
        "(no database yet), and write/list endpoints require a JWT bearer token."
    ),
    version="1.0.0",
)

# Rate limiting (SlowAPI) — bonus feature
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_routes.router)
app.include_router(entries.router)


@app.get("/", tags=["Root"])
def root():
    return {"name": "AquaLog API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}