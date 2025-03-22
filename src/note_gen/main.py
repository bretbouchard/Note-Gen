from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    return {"status": "ok"}

@app.post("/test")
async def test_post_endpoint(request: Request):
    return {"status": "ok"}
