from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic/FastAPI request validation errors.
    Returns user-friendly field-level error messages.
    """
    custom_errors = []
    for error in exc.errors():
        loc = error.get("loc", [])

        if "full_name" in loc:
            err_type = error.get("type", "")
            if err_type == "missing":
                msg = "Full name is required for registration"
            else:
                msg = error.get("msg", "Invalid full name")
                if msg.startswith("Value error, "):
                    msg = msg[len("Value error, "):]
        else:
            msg = error.get("msg", "Validation error")

        custom_errors.append({"field": loc[-1] if loc else "unknown", "message": msg})

    return JSONResponse(status_code=422, content={"detail": custom_errors})
