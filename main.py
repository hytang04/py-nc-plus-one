import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from api.auth import router as auth_router
from api.events import router as events_router

app = FastAPI(title="NC Plus One")
app.include_router(auth_router)
app.include_router(events_router)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches request validation errors (e.g. missing fields, invalid types)
    and formats the response with HTTP 400 Bad Request.
    """
    logging.getLogger(__name__).error(
        "Unhandled exception while processing request",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field is missing or invalid",
            }
        },
    )


@app.exception_handler(Exception)
def handle_unexpected_exception(request: Request, exc: Exception):
    """
    Catches unexpected errors and formats the response
    with HTTP 500 Internal Server Error.
    """
    logging.getLogger(__name__).error(
        "Unhandled exception while processing request",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong",
            }
        },
    )


@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
