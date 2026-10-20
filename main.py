import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from api.events import router as events_router

app = FastAPI(title="NC Plus One")
app.include_router(events_router)


@app.exception_handler(Exception)
def handle_unexpected_exception(request: Request, exc: Exception):
    logging.getLogger(__name__).error(
        "Unhandled exception while processing request",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong",
            }
        },
    )


@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
