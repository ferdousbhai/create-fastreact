from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: Allow all origins
# Security is enforced by Modal's proxy authentication (requires_proxy_auth=True),
# which requires valid Modal-Key and Modal-Secret headers on every request.
# Without valid auth headers, requests are rejected before reaching this code.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/hello")
def hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}
