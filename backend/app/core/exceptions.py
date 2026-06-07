from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError

def add_exception_handlers(app):
    
    @app.exception_handler(IntegrityError)
    async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "A data integrity error occurred."}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "errors": errors}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"Unhandled Exception: {exc}") 
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred."}
        )