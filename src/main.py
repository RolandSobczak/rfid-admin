import sys
import datetime

sys.path.append("..")

from fastapi import FastAPI

from src.routers import tenants

app = FastAPI(description="RFIDIO - Admin API")
app.include_router(tenants.router)
