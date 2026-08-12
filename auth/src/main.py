from fastapi import FastAPI
from src import user,auth,email_endpoint
from contextlib import asynccontextmanager
from db.models import create_tables
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
version = "v1"

app = FastAPI(
    version= version,
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.route, prefix= f"/users/{version}",tags=["Users"])     
app.include_router(auth.route, prefix= f"/auth",tags=["Users"])
app.include_router(email_endpoint.route,tags=["email_endpoint"])