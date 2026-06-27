from fastapi import FastAPI
app = FastAPI(title = "Sentinel AI",version = "0.1")
@app.get("/")
def root():
    return {"message" : "Sentinel is live"}
@app.get("/health")
def health_check():
    return {"status" : "ok", "version" : "0.1"}
