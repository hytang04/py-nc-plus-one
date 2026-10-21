import logging

from fastapi import FastAPI

from api.events import router as events_router

app = FastAPI(title="NC Plus One")
app.include_router(events_router)
