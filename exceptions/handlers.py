from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    处理 HTTPException（如 401、404、400 等）。
    统一返回 {code, message, data: null} 格式。
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail, "data": None},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求参数校验异常（422）。
    提取第一条校验错误信息作为 message。
    """
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    loc = " -> ".join(str(item) for item in first_error.get("loc", []))
    msg = first_error.get("msg", "参数校验失败")
    message = f"{loc}: {msg}" if loc else msg

    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": message, "data": None},
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    处理所有未捕获的异常（500）。
    生产环境不应暴露内部错误详情。
    """
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )
