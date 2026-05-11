from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, code: int = 400, message: str = "请求错误"):
        self.code = code
        self.message = message


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权"):
        super().__init__(code=401, message=message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "无权限"):
        super().__init__(code=403, message=message)


class BadRequestException(AppException):
    def __init__(self, message: str = "参数错误"):
        super().__init__(code=400, message=message)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(status_code=exc.code, content={"code": exc.code, "message": exc.message, "data": None})

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"code": 500, "message": f"服务器内部错误: {str(exc)}", "data": None})
