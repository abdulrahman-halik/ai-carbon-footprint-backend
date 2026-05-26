from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

REQUIRED_FIELD_MESSAGES: dict[str, str] = {
    "full_name": "Full name is required for registration",
    "email": "Email address is required for registration",
    "password": "Password is required for registration",
}

async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Custom handler for Pydantic/FastAPI request validation errors.
    Returns user-friendly field-level error messages.
    """
    custom_errors = []

    for error in exc.errors():
        loc = error.get("loc", [])
        field = loc[-1] if loc else "unknown"
        err_type = error.get("type", "")
        msg = error.get("msg", "Validation error")

        if err_type == "missing" and field in REQUIRED_FIELD_MESSAGES:
            msg = REQUIRED_FIELD_MESSAGES[field]

        if msg.startswith("Value error, "):
            msg = msg.removeprefix("Value error, ")

        custom_errors.append({"field": field, "message": msg})

    return JSONResponse(
        status_code=422,
        content={"detail": custom_errors},
    )