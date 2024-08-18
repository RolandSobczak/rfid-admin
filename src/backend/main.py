import sys
import datetime

sys.path.append("..")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import tenants, deployments, backups
from backend.settings import Settings

settings = Settings()

app = FastAPI(description="RFIDIO - Admin API")
app.include_router(tenants.router)
app.include_router(deployments.router)
app.include_router(backups.router)


# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
