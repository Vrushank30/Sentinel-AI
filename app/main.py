from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routers import router
from app.database import engine
from app import models

models.NodeDB.metadata.create_all(bind=engine)
models.UserDB.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinel AI", version="0.1")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Sentinel AI is alive"}

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1"}