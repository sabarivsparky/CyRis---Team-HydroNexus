"""
REAL LOGIC — Uniform API Error Envelope & Exception Handlers.

Enforces a standard JSON error payload structure for all HTTP exceptions, validation
errors, and internal errors.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("cyris.errors")


from starlette.exceptions import HTTPException as StarletteHTTPException


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[Any] | None = None,
) -> JSONResponse:
    """Construct uniform JSON error response."""
    payload = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        }
    }
    return JSONResponse(status_code=status_code, content=payload)


def register_error_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = exc.errors()
        msg = "Request validation failed."
        if details:
            msg = f"Validation error at {details[0].get('loc', [])}: {details[0].get('msg', '')}"
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="validation_error",
            message=msg,
            details=details,
        )

    @app.exception_handler(HTTPException)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException | StarletteHTTPException) -> JSONResponse:
        code_map = {
            404: "not_found",
            409: "conflict",
            422: "validation_error",
            503: "not_ready",
        }
        code = code_map.get(exc.status_code, "http_error")
        return create_error_response(
            status_code=exc.status_code,
            code=code,
            message=str(exc.detail),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="validation_error",
            message=str(exc),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled server exception: {exc}", exc_info=True)
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_error",
            message="An internal server error occurred.",
        )
