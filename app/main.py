from fastapi import FastAPI
from .routers import entries,authroutes

app = FastAPI(
    title="AquaLog API",
    description=(
        "Track maintenance tasks for home aquariums — feedings, water changes, "
        "filter cleans, and water-parameter checks. Data is stored in memory "
        "(no database yet), and write/list endpoints require a JWT bearer token."
    ),
    version="1.0.0",
)

app.include_router(entries.router)
app.include_router(authroutes.router)

@app.get("/", tags=["Root"])
def root():
    return {"name": "AquaLog API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}