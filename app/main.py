from fastapi import FastAPI
from .database import Base, engine
from .routers import import_router, analysis_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DarkAtlas AI Asset Management",
    version="1.0.0",
    description="AI-powered Attack Surface Management"
)

app.include_router(import_router.router)
app.include_router(analysis_router.router)

@app.get("/")
def root():
    return {"message": "DarkAtlas API is running"}