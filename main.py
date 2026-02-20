from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "msg": "FastAPI is working 🔥"}

@app.get("/test")
def test():
    return {"test": True}