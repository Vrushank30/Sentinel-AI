from fastapi import FastAPI
from app.routers import router
app = FastAPI(title = "Sentinel AI",version = "0.1")
app.include_router(router)
@app.get("/")
def root():
    return {"message" : "Sentinel is live"}
@app.get("/health")
def health_check():
    return {"status" : "ok", "version" : "0.1"}
