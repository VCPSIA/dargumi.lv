from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from app.database import init_db
from app.routes import auth, catalog, collection, recognition, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs("uploads", exist_ok=True)
    yield

app = FastAPI(title="Kolekcija API", version="1.0.0", lifespan=lifespan)

@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    try:
        print(f"[500] {request.method} {request.url.path}\n{tb}")
    except UnicodeEncodeError:
        print(f"[500] {request.method} {request.url.path}\n{tb}".encode("ascii", errors="replace").decode())
    detail = f"{type(exc).__name__}: {exc}"
    return JSONResponse(
        status_code=500,
        content={"detail": detail},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(collection.router)
app.include_router(recognition.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"status": "ok", "app": "Kolekcija API v1.0"}
