# 保健品商家后台管理系统 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零搭建保健品商家后台管理系统，包含商家发布商品/上传资质/提交审核、审核员审核、超管管理品类与用户

**Architecture:** 单体 FastAPI 后端 + 单体 Vue3 前端，按角色模块化组织，JWT 认证，本地文件存储

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0, MySQL, Pydantic v2, Alembic, Vue3, TypeScript, Element Plus, Vite, Pinia, Axios

---

## Phase 1: 后端基础设施

### Task 1: 后端项目脚手架 + 配置

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建 requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
pymysql==1.1.1
alembic==1.13.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
apscheduler==3.10.4
```

- [ ] **Step 2: 创建 backend/app/__init__.py**

```python
```

- [ ] **Step 3: 创建 backend/app/config.py**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    APP_NAME: str = "保健品商家后台管理系统"
    DEBUG: bool = True

    # Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "health_product"
    DATABASE_URL: str = ""

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # File storage
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Scheduler
    QUALIFICATION_EXPIRY_CHECK_DAYS: int = 30

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: 创建 backend/app/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.utils.exceptions import register_exception_handlers
from app.api.auth import router as auth_router
from app.api.upload import router as upload_router
from app.api.categories import router as categories_router
from app.api.merchant.products import router as merchant_product_router
from app.api.merchant.qualifications import router as merchant_qual_router
from app.api.reviewer.products import router as reviewer_router
from app.api.admin.categories import router as admin_category_router
from app.api.admin.merchants import router as admin_merchant_router
from app.api.admin.qualification_types import router as admin_qual_type_router
from app.utils.scheduler import start_scheduler, shutdown_scheduler

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(merchant_product_router, prefix="/api")
app.include_router(merchant_qual_router, prefix="/api")
app.include_router(reviewer_router, prefix="/api")
app.include_router(admin_category_router, prefix="/api")
app.include_router(admin_merchant_router, prefix="/api")
app.include_router(admin_qual_type_router, prefix="/api")
```

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/app/__init__.py backend/app/config.py backend/app/main.py
git commit -m "feat: add backend project scaffold with config"
```

---

### Task 2: 数据库连接 + 基础模型

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/category.py`
- Create: `backend/app/models/qualification_type.py`

- [ ] **Step 1: 创建 backend/app/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: 创建 backend/app/models/__init__.py**

```python
from app.models.user import User
from app.models.category import Category
from app.models.qualification_type import QualificationType
from app.models.product import Product
from app.models.product_compliance import ProductCompliance
from app.models.product_image import ProductImage
from app.models.product_detail import ProductDetail
from app.models.product_qualification import ProductQualification
from app.models.merchant_qualification import MerchantQualification
from app.models.product_version import ProductVersion
from app.models.audit_log import AuditLog
from app.database import Base
```

- [ ] **Step 3: 创建 backend/app/models/user.py**

```python
from datetime import datetime
from sqlalchemy import BigInteger, String, Enum as SAEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    merchant = "merchant"
    reviewer = "reviewer"
    admin = "admin"


class UserStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[UserStatus] = mapped_column(SAEnum(UserStatus), default=UserStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

- [ ] **Step 4: 创建 backend/app/models/category.py**

```python
from datetime import datetime
from sqlalchemy import BigInteger, String, Integer, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.database import Base
import enum


class CategoryStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[CategoryStatus] = mapped_column(SAEnum(CategoryStatus), default=CategoryStatus.active)
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    children: Mapped[List["Category"]] = relationship("Category", backref="parent", remote_side=[id])
```

- [ ] **Step 5: 创建 backend/app/models/qualification_type.py**

```python
from sqlalchemy import BigInteger, String, Boolean, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class QualScope(str, enum.Enum):
    merchant = "merchant"
    product = "product"


class QualificationType(Base):
    __tablename__ = "qualification_types"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="")
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    scope: Mapped[QualScope] = mapped_column(SAEnum(QualScope), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/database.py backend/app/models/
git commit -m "feat: add database connection and base models"
```

---

### Task 3: 商品相关模型

**Files:**
- Create: `backend/app/models/product.py`
- Create: `backend/app/models/product_compliance.py`
- Create: `backend/app/models/product_image.py`
- Create: `backend/app/models/product_detail.py`
- Create: `backend/app/models/product_qualification.py`
- Create: `backend/app/models/merchant_qualification.py`
- Create: `backend/app/models/product_version.py`
- Create: `backend/app/models/audit_log.py`

- [ ] **Step 1: 创建 backend/app/models/product.py**

```python
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import BigInteger, String, Integer, Numeric, Text, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.database import Base
import enum


class ProductStatus(str, enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), default="")
    spec: Mapped[str] = mapped_column(String(100), default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    main_image: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[ProductStatus] = mapped_column(SAEnum(ProductStatus), default=ProductStatus.draft)
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submit_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    audit_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    audit_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    compliance: Mapped[Optional["ProductCompliance"]] = relationship(back_populates="product", uselist=False)
    images: Mapped[List["ProductImage"]] = relationship(back_populates="product")
    detail: Mapped[Optional["ProductDetail"]] = relationship(back_populates="product", uselist=False)
    qualifications: Mapped[List["ProductQualification"]] = relationship(back_populates="product")
    versions: Mapped[List["ProductVersion"]] = relationship(back_populates="product")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="product")
```

- [ ] **Step 2: 创建 backend/app/models/product_compliance.py**

```python
from sqlalchemy import BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProductCompliance(Base):
    __tablename__ = "product_compliances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), unique=True, nullable=False)
    approval_number: Mapped[str] = mapped_column(String(100), default="")
    main_ingredients: Mapped[str] = mapped_column(Text, default="")
    efficacy_ingredients: Mapped[str] = mapped_column(Text, default="")
    suitable_population: Mapped[str] = mapped_column(String(500), default="")
    unsuitable_population: Mapped[str] = mapped_column(String(500), default="")
    health_function: Mapped[str] = mapped_column(String(500), default="")
    usage_dosage: Mapped[str] = mapped_column(String(500), default="")
    shelf_life: Mapped[str] = mapped_column(String(100), default="")
    storage_method: Mapped[str] = mapped_column(String(500), default="")
    precautions: Mapped[str] = mapped_column(Text, default="")

    product: Mapped["Product"] = relationship(back_populates="compliance")
```

- [ ] **Step 3: 创建 backend/app/models/product_image.py**

```python
from sqlalchemy import BigInteger, String, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ImageType(str, enum.Enum):
    main = "main"
    detail = "detail"


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), nullable=False)
    image_type: Mapped[ImageType] = mapped_column(SAEnum(ImageType), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="images")
```

- [ ] **Step 4: 创建 backend/app/models/product_detail.py**

```python
from sqlalchemy import BigInteger, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProductDetail(Base):
    __tablename__ = "product_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")

    product: Mapped["Product"] = relationship(back_populates="detail")
```

- [ ] **Step 5: 创建 backend/app/models/product_qualification.py**

```python
from datetime import datetime, date
from sqlalchemy import BigInteger, String, Date, Enum as SAEnum, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base
import enum


class QualStatus(str, enum.Enum):
    valid = "valid"
    expiring = "expiring"
    expired = "expired"


class ProductQualification(Base):
    __tablename__ = "product_qualifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), nullable=False)
    qual_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("qualification_types.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), default="")
    expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[QualStatus] = mapped_column(SAEnum(QualStatus), default=QualStatus.valid)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="qualifications")
```

- [ ] **Step 6: 创建 backend/app/models/merchant_qualification.py**

```python
from datetime import datetime, date
from sqlalchemy import BigInteger, String, Date, Enum as SAEnum, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.database import Base
from app.models.product_qualification import QualStatus


class MerchantQualification(Base):
    __tablename__ = "merchant_qualifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    qual_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("qualification_types.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), default="")
    expire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[QualStatus] = mapped_column(SAEnum(QualStatus), default=QualStatus.valid)
    remark: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
```

- [ ] **Step 7: 创建 backend/app/models/product_version.py**

```python
from datetime import datetime
from sqlalchemy import BigInteger, Integer, JSON, Enum as SAEnum, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ChangeType(str, enum.Enum):
    submit = "submit"
    approve = "approve"
    reject = "reject"
    resubmit = "resubmit"


class ProductVersion(Base):
    __tablename__ = "product_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    change_type: Mapped[ChangeType] = mapped_column(SAEnum(ChangeType), nullable=False)
    changed_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="versions")
```

- [ ] **Step 8: 创建 backend/app/models/audit_log.py**

```python
from datetime import datetime
from sqlalchemy import BigInteger, Enum as SAEnum, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base
import enum


class AuditAction(str, enum.Enum):
    submit = "submit"
    approve = "approve"
    reject = "reject"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    action: Mapped[AuditAction] = mapped_column(SAEnum(AuditAction), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="audit_logs")
```

- [ ] **Step 9: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add product and audit models"
```

---

### Task 4: 枚举、工具类、异常处理

**Files:**
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/enums.py`
- Create: `backend/app/utils/response.py`
- Create: `backend/app/utils/exceptions.py`
- Create: `backend/app/utils/scheduler.py`

- [ ] **Step 1: 创建 backend/app/utils/__init__.py**

```python
```

- [ ] **Step 2: 创建 backend/app/utils/response.py**

```python
from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any = None


class PageData(BaseModel):
    list: list
    total: int
    page: int
    page_size: int


def success(data: Any = None, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": data}


def error(code: int = 500, message: str = "error", data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}


def page_result(items: list, total: int, page: int, page_size: int) -> dict:
    return success({"list": items, "total": total, "page": page, "page_size": page_size})
```

- [ ] **Step 3: 创建 backend/app/utils/exceptions.py**

```python
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
```

- [ ] **Step 4: 创建 backend/app/utils/scheduler.py**

```python
from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models.merchant_qualification import MerchantQualification, QualStatus
from app.models.product_qualification import ProductQualification
from app.config import get_settings

scheduler = BackgroundScheduler()
settings = get_settings()


def check_qualification_expiry():
    db = SessionLocal()
    try:
        today = date.today()
        warning_date = today + timedelta(days=settings.QUALIFICATION_EXPIRY_CHECK_DAYS)

        for model in [MerchantQualification, ProductQualification]:
            # 即将到期: expire_date <= 30天后 且 还未到期
            db.query(model).filter(
                model.expire_date <= warning_date,
                model.expire_date >= today,
                model.status == QualStatus.valid
            ).update({model.status: QualStatus.expiring})

            # 已过期: expire_date < 今天
            db.query(model).filter(
                model.expire_date < today,
                model.status.in_([QualStatus.valid, QualStatus.expiring])
            ).update({model.status: QualStatus.expired})

        db.commit()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_qualification_expiry, "cron", hour=2, minute=0, id="check_expiry")
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown()
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/
git commit -m "feat: add enums, utils, exceptions, and scheduler"
```

---

## Phase 2: 后端认证与依赖注入

### Task 5: 认证系统

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/dependencies.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/auth.py`

- [ ] **Step 1: 创建 backend/app/schemas/__init__.py**

```python
```

- [ ] **Step 2: 创建 backend/app/schemas/auth.py**

```python
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str
    user_id: int


class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    phone: str
    status: str

    class Config:
        from_attributes = True
```

- [ ] **Step 3: 创建 backend/app/services/__init__.py**

```python
```

- [ ] **Step 4: 创建 backend/app/services/auth_service.py**

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.user import User
from app.utils.exceptions import UnauthorizedException

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise UnauthorizedException("token 无效或已过期")


def authenticate(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedException("用户名或密码错误")
    if user.status.value == "disabled":
        raise UnauthorizedException("账号已被禁用")
    return user
```

- [ ] **Step 5: 创建 backend/app/dependencies.py**

```python
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token
from app.models.user import User
from app.utils.exceptions import UnauthorizedException, ForbiddenException


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException("认证格式错误")
    token = authorization[7:]
    payload = decode_token(token)
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise UnauthorizedException("用户不存在")
    if user.status.value == "disabled":
        raise UnauthorizedException("账号已被禁用")
    return user


def require_merchant(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "merchant":
        raise ForbiddenException("仅商家可操作")
    return user


def require_reviewer(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "reviewer":
        raise ForbiddenException("仅审核员可操作")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.value != "admin":
        raise ForbiddenException("仅超管可操作")
    return user
```

- [ ] **Step 6: 创建 backend/app/api/__init__.py**

```python
```

- [ ] **Step 7: 创建 backend/app/api/auth.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth_service import authenticate, create_token
from app.dependencies import get_current_user
from app.utils.response import success

router = APIRouter(tags=["认证"])


@router.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, req.username, req.password)
    token = create_token(user.id, user.username, user.role.value)
    return success(LoginResponse(token=token, username=user.username, role=user.role.value, user_id=user.id).model_dump())


@router.post("/auth/logout")
def logout(user=Depends(get_current_user)):
    return success(message="已退出")


@router.get("/auth/me")
def me(user=Depends(get_current_user)):
    return success(UserInfo.model_validate(user).model_dump())
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/ backend/app/services/ backend/app/dependencies.py backend/app/api/
git commit -m "feat: add auth system with JWT"
```

---

## Phase 3: 后端核心业务

### Task 6: Schema 定义

**Files:**
- Create: `backend/app/schemas/product.py`
- Create: `backend/app/schemas/qualification.py`
- Create: `backend/app/schemas/category.py`
- Create: `backend/app/schemas/audit.py`

- [ ] **Step 1: 创建 backend/app/schemas/category.py**

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryCreate(BaseModel):
    parent_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


class CategoryInfo(BaseModel):
    id: int
    parent_id: Optional[int]
    name: str
    description: str
    sort_order: int
    status: str
    children: List["CategoryInfo"] = []

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 创建 backend/app/schemas/product.py**

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductComplianceSchema(BaseModel):
    approval_number: str = ""
    main_ingredients: str = ""
    efficacy_ingredients: str = ""
    suitable_population: str = ""
    unsuitable_population: str = ""
    health_function: str = ""
    usage_dosage: str = ""
    shelf_life: str = ""
    storage_method: str = ""
    precautions: str = ""


class ProductImageSchema(BaseModel):
    id: Optional[int] = None
    image_type: str
    file_url: str
    sort_order: int = 0

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=200)
    brand: str = ""
    spec: str = ""
    price: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    main_image: str = ""


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = None
    spec: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    main_image: Optional[str] = None
    compliance: Optional[ProductComplianceSchema] = None


class ProductListInfo(BaseModel):
    id: int
    name: str
    brand: str
    category_name: str = ""
    price: Decimal
    stock: int
    main_image: str
    status: str
    submit_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetailInfo(BaseModel):
    id: int
    merchant_id: int
    category_id: int
    name: str
    brand: str
    spec: str
    price: Decimal
    stock: int
    main_image: str
    status: str
    reject_reason: Optional[str] = None
    submit_at: Optional[datetime] = None
    audit_at: Optional[datetime] = None
    audit_by: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: datetime
    compliance: Optional[ProductComplianceSchema] = None
    images: List[ProductImageSchema] = []
    detail: Optional[str] = None

    class Config:
        from_attributes = True


class ProductSubmitResponse(BaseModel):
    id: int
    status: str
    version: int
```

- [ ] **Step 3: 创建 backend/app/schemas/qualification.py**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class QualificationCreate(BaseModel):
    qual_type_id: int
    file_url: str
    file_name: str = ""
    expire_date: Optional[date] = None


class QualificationUpdate(BaseModel):
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    expire_date: Optional[date] = None


class QualificationInfo(BaseModel):
    id: int
    qual_type_id: int
    qual_type_name: str = ""
    file_url: str
    file_name: str
    expire_date: Optional[date] = None
    status: str
    remark: str = ""
    created_at: datetime

    class Config:
        from_attributes = True


class QualificationTypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: str = ""
    is_required: bool = True
    scope: str = "merchant"
    sort_order: int = 0


class QualificationTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    scope: Optional[str] = None
    sort_order: Optional[int] = None


class QualificationTypeInfo(BaseModel):
    id: int
    name: str
    code: str
    description: str
    is_required: bool
    scope: str
    sort_order: int

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_products: int = 0
    pending_products: int = 0
    approved_products: int = 0
    rejected_products: int = 0
    expiring_quals: int = 0
    expired_quals: int = 0
```

- [ ] **Step 4: 创建 backend/app/schemas/audit.py**

```python
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1, message="驳回原因不能为空")


class BatchIdsRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, message="至少选择一个商品")


class AuditLogInfo(BaseModel):
    id: int
    reviewer_id: int
    action: str
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VersionInfo(BaseModel):
    id: int
    version: int
    change_type: str
    changed_by: int
    remark: str
    created_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas/
git commit -m "feat: add Pydantic schemas"
```

---

### Task 7: 业务服务层

**Files:**
- Create: `backend/app/services/product_service.py`
- Create: `backend/app/services/qualification_service.py`
- Create: `backend/app/services/audit_service.py`
- Create: `backend/app/services/version_service.py`

- [ ] **Step 1: 创建 backend/app/services/product_service.py**

```python
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import Optional
import json

from app.models.product import Product, ProductStatus
from app.models.product_compliance import ProductCompliance
from app.models.product_image import ProductImage
from app.models.product_detail import ProductDetail
from app.schemas.product import ProductCreate, ProductUpdate, ProductComplianceSchema
from app.utils.exceptions import NotFoundException, BadRequestException


def list_products(
    db: Session, merchant_id: int,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1, page_size: int = 20
):
    q = db.query(Product).filter(Product.merchant_id == merchant_id)
    if status:
        q = q.filter(Product.status == status)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    total = q.count()
    items = q.order_by(Product.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_product(db: Session, product_id: int, merchant_id: Optional[int] = None) -> Product:
    q = db.query(Product).options(
        joinedload(Product.compliance),
        joinedload(Product.images),
        joinedload(Product.detail),
        joinedload(Product.qualifications),
    ).filter(Product.id == product_id)
    if merchant_id:
        q = q.filter(Product.merchant_id == merchant_id)
    product = q.first()
    if not product:
        raise NotFoundException("商品不存在")
    return product


def create_product(db: Session, merchant_id: int, data: ProductCreate) -> Product:
    product = Product(merchant_id=merchant_id, **data.model_dump())
    db.add(product)
    db.flush()
    # 同时创建空的 compliance 和 detail 记录
    db.add(ProductCompliance(product_id=product.id))
    db.add(ProductDetail(product_id=product.id))
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    compliance_data = None
    if data.compliance:
        compliance_data = data.compliance
        data = data.model_dump(exclude={"compliance"}, exclude_unset=True)
    else:
        data = data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(product, field, value)

    if compliance_data:
        comp = db.query(ProductCompliance).filter(ProductCompliance.product_id == product.id).first()
        for field, value in compliance_data.model_dump().items():
            setattr(comp, field, value)

    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product):
    if product.status != ProductStatus.draft:
        raise BadRequestException("仅草稿状态可删除")
    db.delete(product)
    db.commit()


def build_product_snapshot(product: Product) -> dict:
    """构建商品完整快照"""
    product_dict = {
        "name": product.name, "brand": product.brand, "spec": product.spec,
        "price": str(product.price), "stock": product.stock, "main_image": product.main_image,
        "category_id": product.category_id,
    }
    if product.compliance:
        product_dict["compliance"] = {c.name: getattr(product.compliance, c.name) for c in product.compliance.__table__.columns if c.name not in ("id", "product_id")}
    if product.images:
        product_dict["images"] = [{"image_type": img.image_type.value, "file_url": img.file_url, "sort_order": img.sort_order} for img in product.images]
    if product.detail:
        product_dict["detail"] = product.detail.content
    return product_dict
```

- [ ] **Step 2: 创建 backend/app/services/qualification_service.py**

```python
from sqlalchemy.orm import Session
from app.models.merchant_qualification import MerchantQualification, QualStatus
from app.models.product_qualification import ProductQualification
from app.models.qualification_type import QualificationType
from app.utils.exceptions import NotFoundException


def list_merchant_qualifications(db: Session, merchant_id: int):
    return db.query(MerchantQualification).filter(MerchantQualification.merchant_id == merchant_id).order_by(MerchantQualification.created_at.desc()).all()


def get_merchant_qualification(db: Session, qual_id: int, merchant_id: int):
    q = db.query(MerchantQualification).filter(MerchantQualification.id == qual_id, MerchantQualification.merchant_id == merchant_id).first()
    if not q:
        raise NotFoundException("资质不存在")
    return q


def create_merchant_qualification(db: Session, merchant_id: int, qual_type_id: int, file_url: str, file_name: str = "", expire_date=None):
    q = MerchantQualification(merchant_id=merchant_id, qual_type_id=qual_type_id, file_url=file_url, file_name=file_name, expire_date=expire_date)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def update_merchant_qualification(db: Session, qual: MerchantQualification, file_url=None, file_name=None, expire_date=None):
    if file_url:
        qual.file_url = file_url
    if file_name:
        qual.file_name = file_name
    qual.expire_date = expire_date
    db.commit()
    return qual


def delete_merchant_qualification(db: Session, qual: MerchantQualification):
    db.delete(qual)
    db.commit()


def list_product_qualifications(db: Session, product_id: int):
    return db.query(ProductQualification).filter(ProductQualification.product_id == product_id).order_by(ProductQualification.created_at.desc()).all()


def create_product_qualification(db: Session, product_id: int, qual_type_id: int, file_url: str, file_name: str = "", expire_date=None):
    q = ProductQualification(product_id=product_id, qual_type_id=qual_type_id, file_url=file_url, file_name=file_name, expire_date=expire_date)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def get_product_qualification(db: Session, qual_id: int, product_id: int):
    q = db.query(ProductQualification).filter(ProductQualification.id == qual_id, ProductQualification.product_id == product_id).first()
    if not q:
        raise NotFoundException("资质不存在")
    return q


def delete_product_qualification(db: Session, qual: ProductQualification):
    db.delete(qual)
    db.commit()
```

- [ ] **Step 3: 创建 backend/app/services/audit_service.py**

```python
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import Optional, List

from app.models.product import Product, ProductStatus
from app.models.audit_log import AuditLog, AuditAction
from app.models.product_version import ProductVersion, ChangeType
from app.utils.exceptions import NotFoundException, BadRequestException
from app.services.product_service import build_product_snapshot


def list_review_products(db: Session, status: Optional[str] = None, category_id: Optional[int] = None,
                         merchant_id: Optional[int] = None, keyword: Optional[str] = None,
                         date_from: Optional[str] = None, date_to: Optional[str] = None,
                         page: int = 1, page_size: int = 20, sort_by: str = "submit_at"):
    q = db.query(Product).filter(Product.status.in_([ProductStatus.pending_review, ProductStatus.approved, ProductStatus.rejected]))
    if status:
        q = q.filter(Product.status == status)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if merchant_id:
        q = q.filter(Product.merchant_id == merchant_id)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    if date_from:
        q = q.filter(Product.submit_at >= datetime.fromisoformat(date_from))
    if date_to:
        q = q.filter(Product.submit_at <= datetime.fromisoformat(date_to))

    if sort_by == "submit_at":
        q = q.order_by(Product.submit_at.desc())
    else:
        q = q.order_by(Product.updated_at.desc())

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def approve_product(db: Session, product: Product, reviewer_id: int):
    if product.status != ProductStatus.pending_review:
        raise BadRequestException("仅待审核商品可通过")
    product.status = ProductStatus.approved
    product.audit_at = datetime.utcnow()
    product.audit_by = reviewer_id
    product.version += 1
    product.updated_at = datetime.utcnow()

    snapshot = build_product_snapshot(product)
    db.add(AuditLog(product_id=product.id, reviewer_id=reviewer_id, action=AuditAction.approve))
    db.add(ProductVersion(product_id=product.id, version=product.version, snapshot_json=snapshot,
                          change_type=ChangeType.approve, changed_by=reviewer_id))
    db.commit()
    return product


def reject_product(db: Session, product: Product, reviewer_id: int, reason: str):
    if product.status != ProductStatus.pending_review:
        raise BadRequestException("仅待审核商品可驳回")
    product.status = ProductStatus.rejected
    product.reject_reason = reason
    product.audit_at = datetime.utcnow()
    product.audit_by = reviewer_id
    product.version += 1
    product.updated_at = datetime.utcnow()

    snapshot = build_product_snapshot(product)
    db.add(AuditLog(product_id=product.id, reviewer_id=reviewer_id, action=AuditAction.reject, reason=reason))
    db.add(ProductVersion(product_id=product.id, version=product.version, snapshot_json=snapshot,
                          change_type=ChangeType.reject, changed_by=reviewer_id, remark=reason))
    db.commit()
    return product


def batch_approve(db: Session, product_ids: List[int], reviewer_id: int):
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.status == ProductStatus.pending_review).all()
    for p in products:
        approve_product(db, p, reviewer_id)
    return len(products)


def batch_reject(db: Session, product_ids: List[int], reviewer_id: int, reason: str):
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.status == ProductStatus.pending_review).all()
    for p in products:
        reject_product(db, p, reviewer_id, reason)
    return len(products)
```

- [ ] **Step 4: 创建 backend/app/services/version_service.py**

```python
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.product_version import ProductVersion, ChangeType
from app.models.product import Product
from app.services.product_service import build_product_snapshot


def save_version(db: Session, product: Product, change_type: ChangeType, changed_by: int, remark: str = ""):
    snapshot = build_product_snapshot(product)
    version = ProductVersion(
        product_id=product.id, version=product.version, snapshot_json=snapshot,
        change_type=change_type, changed_by=changed_by, remark=remark
    )
    db.add(version)
    db.flush()
    return version


def get_versions(db: Session, product_id: int):
    return db.query(ProductVersion).filter(ProductVersion.product_id == product_id).order_by(ProductVersion.created_at.desc()).all()
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/
git commit -m "feat: add business service layer"
```

---

### Task 8: 商家端 API — 商品管理

**Files:**
- Create: `backend/app/api/merchant/__init__.py`
- Create: `backend/app/api/merchant/products.py`

- [ ] **Step 1: 创建 backend/app/api/merchant/__init__.py**

```python
```

- [ ] **Step 2: 创建 backend/app/api/merchant/products.py** — 商品 CRUD + 提交

```python
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.dependencies import require_merchant
from app.models.user import User
from app.models.product import Product, ProductStatus
from app.models.product_image import ProductImage, ImageType
from app.models.product_version import ChangeType
from app.schemas.product import ProductCreate, ProductUpdate, ProductListInfo, ProductDetailInfo, ProductSubmitResponse, ProductImageSchema
from app.services.product_service import list_products, get_product, create_product, update_product, delete_product, build_product_snapshot
from app.services.qualification_service import list_product_qualifications, create_product_qualification, get_product_qualification, delete_product_qualification
from app.services.version_service import save_version, get_versions
from app.schemas.qualification import QualificationCreate, QualificationInfo
from app.schemas.audit import VersionInfo
from app.utils.response import success, page_result
from app.utils.exceptions import BadRequestException, NotFoundException

router = APIRouter(tags=["商家-商品"])


@router.get("/merchant/products")
def merchant_product_list(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(require_merchant),
):
    items, total = list_products(db, user.id, status, keyword, page, page_size)
    result = []
    for p in items:
        result.append(ProductListInfo(
            id=p.id, name=p.name, brand=p.brand,
            category_name=p.category_id, price=p.price,
            stock=p.stock, main_image=p.main_image, status=p.status.value,
            submit_at=p.submit_at, created_at=p.created_at,
            category_name="",
        ))
    return page_result(result, total, page, page_size)


@router.post("/merchant/products")
def merchant_product_create(data: ProductCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    product = create_product(db, user.id, data)
    return success({"id": product.id, "status": product.status.value})


@router.get("/merchant/products/{product_id}")
def merchant_product_detail(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    p = get_product(db, product_id, user.id)
    compliance = None
    if p.compliance:
        compliance = {c.name: getattr(p.compliance, c.name) for c in p.compliance.__table__.columns if c.name not in ("id", "product_id")}
    return success(ProductDetailInfo(
        id=p.id, merchant_id=p.merchant_id, category_id=p.category_id,
        name=p.name, brand=p.brand, spec=p.spec,
        price=p.price, stock=p.stock, main_image=p.main_image,
        status=p.status.value, reject_reason=p.reject_reason,
        submit_at=p.submit_at, audit_at=p.audit_at, audit_by=p.audit_by,
        version=p.version, created_at=p.created_at, updated_at=p.updated_at,
        compliance=compliance,
        images=[ProductImageSchema.model_validate(img) for img in (p.images or [])],
        detail=p.detail.content if p.detail else None,
    ))


@router.put("/merchant/products/{product_id}")
def merchant_product_update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    p = get_product(db, product_id, user.id)
    product = update_product(db, p, data)
    return success({"id": product.id, "status": product.status.value})


@router.delete("/merchant/products/{product_id}")
def merchant_product_delete(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    p = get_product(db, product_id, user.id)
    delete_product(db, p)
    return success(message="删除成功")


@router.post("/merchant/products/{product_id}/submit")
def merchant_product_submit(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    p = get_product(db, product_id, user.id)
    if p.status != ProductStatus.draft and p.status != ProductStatus.rejected:
        raise BadRequestException("仅草稿或驳回状态可提交审核")
    p.status = ProductStatus.pending_review
    p.submit_at = datetime.utcnow()
    p.updated_at = datetime.utcnow()
    save_version(db, p, ChangeType.submit if p.status == ProductStatus.pending_review else ChangeType.resubmit, user.id)
    db.commit()
    return success(ProductSubmitResponse(id=p.id, status=p.status.value, version=p.version))
```

- [ ] **Step 3: 在 backend/app/api/merchant/products.py 追加商品图片管理接口**

```python
@router.post("/merchant/products/{product_id}/images")
def merchant_product_add_image(product_id: int, image: ProductImageSchema, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    p = get_product(db, product_id, user.id)
    img = ProductImage(product_id=p.id, image_type=ImageType(image.image_type), file_url=image.file_url, sort_order=image.sort_order)
    db.add(img)
    db.commit()
    return success({"id": img.id})


@router.delete("/merchant/products/{product_id}/images/{image_id}")
def merchant_product_delete_image(product_id: int, image_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    get_product(db, product_id, user.id)
    img = db.query(ProductImage).filter(ProductImage.id == image_id, ProductImage.product_id == product_id).first()
    if not img:
        raise NotFoundException("图片不存在")
    db.delete(img)
    db.commit()
    return success(message="删除成功")
```

- [ ] **Step 4: 在 backend/app/api/merchant/products.py 追加版本历史和商品资质接口**

```python
@router.get("/merchant/products/{product_id}/versions")
def merchant_product_versions(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    get_product(db, product_id, user.id)
    versions = get_versions(db, product_id)
    return success([VersionInfo.model_validate(v) for v in versions])


@router.get("/merchant/products/{product_id}/qualifications")
def merchant_product_qual_list(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    get_product(db, product_id, user.id)
    quals = list_product_qualifications(db, product_id)
    return success([QualificationInfo.model_validate(q) for q in quals])


@router.post("/merchant/products/{product_id}/qualifications")
def merchant_product_qual_create(product_id: int, data: QualificationCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    get_product(db, product_id, user.id)
    q = create_product_qualification(db, product_id, data.qual_type_id, data.file_url, data.file_name, data.expire_date)
    return success({"id": q.id})


@router.delete("/merchant/products/{product_id}/qualifications/{qual_id}")
def merchant_product_qual_delete(product_id: int, qual_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    get_product(db, product_id, user.id)
    q = get_product_qualification(db, qual_id, product_id)
    delete_product_qualification(db, q)
    return success(message="删除成功")
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/merchant/
git commit -m "feat: add merchant product APIs"
```

---

### Task 9: 商家端 API — 资质管理 + Dashboard

**Files:**
- Create: `backend/app/api/merchant/qualifications.py`
- Modify: `backend/app/api/merchant/products.py` (追加 dashboard)

- [ ] **Step 1: 创建 backend/app/api/merchant/qualifications.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_merchant
from app.models.user import User
from app.schemas.qualification import QualificationCreate, QualificationUpdate, QualificationInfo
from app.services.qualification_service import (
    list_merchant_qualifications, get_merchant_qualification,
    create_merchant_qualification, update_merchant_qualification, delete_merchant_qualification
)
from app.utils.response import success

router = APIRouter(tags=["商家-资质"])


@router.get("/merchant/qualifications")
def merchant_qual_list(db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    quals = list_merchant_qualifications(db, user.id)
    return success([QualificationInfo.model_validate(q) for q in quals])


@router.post("/merchant/qualifications")
def merchant_qual_create(data: QualificationCreate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    q = create_merchant_qualification(db, user.id, data.qual_type_id, data.file_url, data.file_name, data.expire_date)
    return success({"id": q.id})


@router.put("/merchant/qualifications/{qual_id}")
def merchant_qual_update(qual_id: int, data: QualificationUpdate, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    q = get_merchant_qualification(db, qual_id, user.id)
    update_merchant_qualification(db, q, data.file_url, data.file_name, data.expire_date)
    return success(message="更新成功")


@router.delete("/merchant/qualifications/{qual_id}")
def merchant_qual_delete(qual_id: int, db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    q = get_merchant_qualification(db, qual_id, user.id)
    delete_merchant_qualification(db, q)
    return success(message="删除成功")
```

- [ ] **Step 2: 在 backend/app/api/merchant/products.py 追加 dashboard 接口**

在文件末尾添加：

```python
@router.get("/merchant/dashboard")
def merchant_dashboard(db: Session = Depends(get_db), user: User = Depends(require_merchant)):
    from app.models.merchant_qualification import MerchantQualification
    total = db.query(Product).filter(Product.merchant_id == user.id).count()
    pending = db.query(Product).filter(Product.merchant_id == user.id, Product.status == ProductStatus.pending_review).count()
    approved = db.query(Product).filter(Product.merchant_id == user.id, Product.status == ProductStatus.approved).count()
    rejected = db.query(Product).filter(Product.merchant_id == user.id, Product.status == ProductStatus.rejected).count()
    expiring = db.query(MerchantQualification).filter(MerchantQualification.merchant_id == user.id, MerchantQualification.status == "expiring").count()
    expired = db.query(MerchantQualification).filter(MerchantQualification.merchant_id == user.id, MerchantQualification.status == "expired").count()
    return success({
        "total_products": total, "pending_products": pending,
        "approved_products": approved, "rejected_products": rejected,
        "expiring_quals": expiring, "expired_quals": expired,
    })
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/merchant/
git commit -m "feat: add merchant qualification and dashboard APIs"
```

---

### Task 10: 公共接口 + 文件上传

**Files:**
- Create: `backend/app/api/categories.py`
- Create: `backend/app/api/upload.py`

- [ ] **Step 1: 创建 backend/app/api/categories.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category, CategoryStatus
from app.schemas.category import CategoryInfo
from app.utils.response import success

router = APIRouter(tags=["品类字典"])


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).filter(Category.status == CategoryStatus.active).order_by(Category.sort_order).all()
    # 构建品类树
    result = []
    for cat in categories:
        if cat.parent_id is None:
            result.append(_build_tree(cat, categories))
    return success(result)


def _build_tree(cat: Category, all_cats: list) -> dict:
    children = [_build_tree(c, all_cats) for c in all_cats if c.parent_id == cat.id]
    info = CategoryInfo.model_validate(cat)
    info.children = children
    return info.model_dump()


@router.get("/qualification-types")
def get_qualification_types(scope: str = None, db: Session = Depends(get_db)):
    from app.models.qualification_type import QualificationType
    q = db.query(QualificationType)
    if scope:
        q = q.filter(QualificationType.scope == scope)
    items = q.order_by(QualificationType.sort_order).all()
    return success([{"id": t.id, "name": t.name, "code": t.code, "description": t.description, "is_required": t.is_required, "scope": t.scope.value, "sort_order": t.sort_order} for t in items])
```

- [ ] **Step 2: 创建 backend/app/api/upload.py**

```python
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends
from app.config import get_settings
from app.dependencies import get_current_user
from app.utils.response import success, error
from app.utils.exceptions import BadRequestException

settings = get_settings()
router = APIRouter(tags=["文件上传"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_FILE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"}


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise BadRequestException("仅支持 JPG/PNG/GIF/WebP 图片格式")
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException("文件大小不能超过 10MB")

    ext = os.path.splitext(file.filename or ".jpg")[1] or ".jpg"
    today = datetime.now().strftime("%Y%m%d")
    relative_path = f"images/{today}/{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    content = await file.read()
    with open(full_path, "wb") as f:
        f.write(content)

    return success({"url": f"/uploads/{relative_path}", "name": file.filename})


@router.post("/upload/file")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise BadRequestException("仅支持 JPG/PNG/GIF/WebP/PDF 格式")
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException("文件大小不能超过 10MB")

    ext = os.path.splitext(file.filename or ".pdf")[1] or ".pdf"
    today = datetime.now().strftime("%Y%m%d")
    relative_path = f"files/{today}/{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    content = await file.read()
    with open(full_path, "wb") as f:
        f.write(content)

    return success({"url": f"/uploads/{relative_path}", "name": file.filename})
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/categories.py backend/app/api/upload.py
git commit -m "feat: add public categories and file upload APIs"
```

---

### Task 11: 审核员端 API

**Files:**
- Create: `backend/app/api/reviewer/__init__.py`
- Create: `backend/app/api/reviewer/products.py`

- [ ] **Step 1: 创建 backend/app/api/reviewer/__init__.py**

```python
```

- [ ] **Step 2: 创建 backend/app/api/reviewer/products.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.dependencies import require_reviewer
from app.models.user import User
from app.models.product import Product, ProductStatus
from app.schemas.audit import RejectRequest, BatchIdsRequest
from app.schemas.product import ProductListInfo, ProductDetailInfo, ProductImageSchema
from app.services.audit_service import list_review_products, approve_product, reject_product, batch_approve, batch_reject
from app.services.product_service import get_product
from app.utils.response import success, page_result
from app.utils.exceptions import NotFoundException

router = APIRouter(tags=["审核员"])


@router.get("/reviewer/products")
def reviewer_product_list(
    status: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    merchant_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("submit_at"),
    db: Session = Depends(get_db),
    user: User = Depends(require_reviewer),
):
    items, total = list_review_products(db, status, category_id, merchant_id, keyword, date_from, date_to, page, page_size, sort_by)
    result = []
    for p in items:
        result.append(ProductListInfo(
            id=p.id, name=p.name, brand=p.brand,
            category_name="", price=p.price,
            stock=p.stock, main_image=p.main_image, status=p.status.value,
            submit_at=p.submit_at, created_at=p.created_at,
        ))
    return page_result(result, total, page, page_size)


@router.get("/reviewer/products/{product_id}")
def reviewer_product_detail(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_reviewer)):
    p = get_product(db, product_id)
    compliance = None
    if p.compliance:
        compliance = {c.name: getattr(p.compliance, c.name) for c in p.compliance.__table__.columns if c.name not in ("id", "product_id")}
    return success(ProductDetailInfo(
        id=p.id, merchant_id=p.merchant_id, category_id=p.category_id,
        name=p.name, brand=p.brand, spec=p.spec,
        price=p.price, stock=p.stock, main_image=p.main_image,
        status=p.status.value, reject_reason=p.reject_reason,
        submit_at=p.submit_at, audit_at=p.audit_at, audit_by=p.audit_by,
        version=p.version, created_at=p.created_at, updated_at=p.updated_at,
        compliance=compliance,
        images=[ProductImageSchema.model_validate(img) for img in (p.images or [])],
        detail=p.detail.content if p.detail else None,
    ))


@router.post("/reviewer/products/{product_id}/approve")
def reviewer_product_approve(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_reviewer)):
    p = get_product(db, product_id)
    approve_product(db, p, user.id)
    return success(message="审核通过")


@router.post("/reviewer/products/{product_id}/reject")
def reviewer_product_reject(product_id: int, req: RejectRequest, db: Session = Depends(get_db), user: User = Depends(require_reviewer)):
    p = get_product(db, product_id)
    reject_product(db, p, user.id, req.reason)
    return success(message="已驳回")


@router.post("/reviewer/products/batch-approve")
def reviewer_batch_approve(req: BatchIdsRequest, db: Session = Depends(get_db), user: User = Depends(require_reviewer)):
    count = batch_approve(db, req.ids, user.id)
    return success({"count": count})


@router.post("/reviewer/products/batch-reject")
def reviewer_batch_reject(req: BatchIdsRequest, reason: str = Query(...), db: Session = Depends(get_db), user: User = Depends(require_reviewer)):
    count = batch_reject(db, req.ids, user.id, reason)
    return success({"count": count})


@router.get("/reviewer/dashboard")
def reviewer_dashboard(db: Session = Depends(get_db), user: User = Depends(require_reviewer)):
    pending = db.query(Product).filter(Product.status == ProductStatus.pending_review).count()
    approved_today = db.query(Product).filter(Product.status == ProductStatus.approved, Product.audit_by == user.id).count()
    rejected_today = db.query(Product).filter(Product.status == ProductStatus.rejected, Product.audit_by == user.id).count()
    return success({"pending_count": pending, "approved_today": approved_today, "rejected_today": rejected_today})
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/api/reviewer/
git commit -m "feat: add reviewer APIs"
```

---

### Task 12: 超管端 API

**Files:**
- Create: `backend/app/api/admin/__init__.py`
- Create: `backend/app/api/admin/categories.py`
- Create: `backend/app/api/admin/merchants.py`
- Create: `backend/app/api/admin/qualification_types.py`

- [ ] **Step 1: 创建 backend/app/api/admin/__init__.py**

```python
```

- [ ] **Step 2: 创建 backend/app/api/admin/categories.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.category import Category, CategoryStatus
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryInfo
from app.utils.response import success
from app.utils.exceptions import NotFoundException

router = APIRouter(tags=["超管-品类"])


@router.post("/admin/categories")
def admin_category_create(data: CategoryCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    cat = Category(parent_id=data.parent_id, name=data.name, description=data.description,
                   sort_order=data.sort_order, created_by=user.id)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return success({"id": cat.id})


@router.put("/admin/categories/{cat_id}")
def admin_category_update(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise NotFoundException("品类不存在")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cat, field, value)
    db.commit()
    return success(message="更新成功")


@router.delete("/admin/categories/{cat_id}")
def admin_category_delete(cat_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise NotFoundException("品类不存在")
    # 检查是否有子品类
    children = db.query(Category).filter(Category.parent_id == cat_id).count()
    if children:
        return success(code=400, message="请先删除子品类")
    db.delete(cat)
    db.commit()
    return success(message="删除成功")
```

- [ ] **Step 3: 创建 backend/app/api/admin/merchants.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User, UserRole, UserStatus
from app.services.auth_service import hash_password
from app.utils.response import success, page_result
from app.utils.exceptions import NotFoundException

router = APIRouter(tags=["超管-商家"])


@router.get("/admin/merchants")
def admin_merchant_list(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        db: Session = Depends(get_db), user: User = Depends(require_admin)):
    q = db.query(User).filter(User.role == UserRole.merchant)
    total = q.count()
    items = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return page_result([{"id": u.id, "username": u.username, "phone": u.phone, "status": u.status.value, "created_at": u.created_at.isoformat()} for u in items], total, page, page_size)


@router.put("/admin/merchants/{merchant_id}/status")
def admin_merchant_status(merchant_id: int, status: str = Query(...), db: Session = Depends(get_db), user: User = Depends(require_admin)):
    m = db.query(User).filter(User.id == merchant_id, User.role == UserRole.merchant).first()
    if not m:
        raise NotFoundException("商家不存在")
    m.status = UserStatus(status)
    db.commit()
    return success(message="更新成功")


@router.get("/admin/reviewers")
def admin_reviewer_list(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
                        db: Session = Depends(get_db), user: User = Depends(require_admin)):
    q = db.query(User).filter(User.role == UserRole.reviewer)
    total = q.count()
    items = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return page_result([{"id": u.id, "username": u.username, "phone": u.phone, "status": u.status.value, "created_at": u.created_at.isoformat()} for u in items], total, page, page_size)


@router.post("/admin/reviewers")
def admin_reviewer_create(username: str = Query(...), password: str = Query(...), phone: str = Query(""),
                          db: Session = Depends(get_db), user: User = Depends(require_admin)):
    exists = db.query(User).filter(User.username == username).first()
    if exists:
        return success(code=400, message="用户名已存在")
    reviewer = User(username=username, password_hash=hash_password(password), role=UserRole.reviewer, phone=phone)
    db.add(reviewer)
    db.commit()
    return success({"id": reviewer.id})
```

- [ ] **Step 4: 创建 backend/app/api/admin/qualification_types.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.qualification_type import QualificationType, QualScope
from app.schemas.qualification import QualificationTypeCreate, QualificationTypeUpdate, QualificationTypeInfo
from app.utils.response import success
from app.utils.exceptions import NotFoundException

router = APIRouter(tags=["超管-资质类型"])


@router.get("/admin/qualification-types")
def admin_qual_type_list(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    items = db.query(QualificationType).order_by(QualificationType.sort_order).all()
    return success([QualificationTypeInfo.model_validate(t) for t in items])


@router.post("/admin/qualification-types")
def admin_qual_type_create(data: QualificationTypeCreate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    t = QualificationType(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return success({"id": t.id})


@router.put("/admin/qualification-types/{type_id}")
def admin_qual_type_update(type_id: int, data: QualificationTypeUpdate, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    t = db.query(QualificationType).filter(QualificationType.id == type_id).first()
    if not t:
        raise NotFoundException("资质类型不存在")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(t, field, value)
    db.commit()
    return success(message="更新成功")


@router.delete("/admin/qualification-types/{type_id}")
def admin_qual_type_delete(type_id: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    t = db.query(QualificationType).filter(QualificationType.id == type_id).first()
    if not t:
        raise NotFoundException("资质类型不存在")
    db.delete(t)
    db.commit()
    return success(message="删除成功")
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/admin/
git commit -m "feat: add admin APIs"
```

---

### Task 13: Alembic 迁移配置 + 种子数据

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/script.py.mako`
- Create: `backend/seed.py`

- [ ] **Step 1: 初始化 Alembic** 并创建迁移

```bash
cd backend && pip install alembic pymysql && alembic init alembic
```

- [ ] **Step 2: 修改 backend/alembic/env.py** — 配置数据库连接

```python
from app.config import get_settings
from app.database import Base
from app.models import *  # noqa: 确保所有模型被导入

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.db_url)
target_metadata = Base.metadata
```

- [ ] **Step 3: 创建种子数据脚本 backend/seed.py**

```python
"""初始化种子数据：admin 账号、默认品类、默认资质类型"""
from app.database import SessionLocal, engine, Base
from app.models import *
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category, CategoryStatus
from app.models.qualification_type import QualificationType, QualScope
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 创建默认角色用户
if not db.query(User).filter(User.username == "admin").first():
    db.add(User(username="admin", password_hash=hash_password("admin123"), role=UserRole.admin))

if not db.query(User).filter(User.username == "reviewer").first():
    db.add(User(username="reviewer", password_hash=hash_password("review123"), role=UserRole.reviewer))

if not db.query(User).filter(User.username == "merchant").first():
    db.add(User(username="merchant", password_hash=hash_password("merchant123"), role=UserRole.merchant))

# 创建默认品类
default_categories = [
    ("增强免疫", "免疫调节类保健品"),
    ("维生素与矿物质", "维生素、矿物质补充剂"),
    ("骨骼健康", "钙片、氨糖等骨骼关节保健品"),
    ("心脑血管", "鱼油、卵磷脂等心脑血管保健品"),
    ("肠道调理", "益生菌、膳食纤维等肠道保健品"),
    ("运动营养", "蛋白粉、氨基酸等运动营养品"),
    ("睡眠助眠", "褪黑素等助眠保健品"),
    ("美容养颜", "胶原蛋白、葡萄籽等美容保健品"),
]
for name, desc in default_categories:
    if not db.query(Category).filter(Category.name == name).first():
        db.add(Category(name=name, description=desc, created_by=1))

# 创建默认资质类型
default_qual_types = [
    ("营业执照", "business_license", "企业营业执照", True, "merchant"),
    ("食品经营许可证", "food_license", "食品经营许可证", True, "merchant"),
    ("法人身份证", "legal_id", "法定代表人身份证", True, "merchant"),
    ("蓝帽批文", "blue_hat_approval", "保健食品批准证书", True, "product"),
    ("检测报告", "test_report", "第三方检测报告", True, "product"),
    ("生产许可证", "production_license", "生产许可证", False, "product"),
    ("品牌授权书", "brand_auth", "品牌授权书", False, "product"),
    ("进口报关单", "customs_declaration", "进口报关单（跨境保健品）", False, "product"),
    ("广告审查表", "ad_review", "广告审查表", False, "product"),
]
for i, (name, code, desc, required, scope) in enumerate(default_qual_types):
    if not db.query(QualificationType).filter(QualificationType.code == code).first():
        db.add(QualificationType(name=name, code=code, description=desc, is_required=required, scope=QualScope(scope), sort_order=i))

db.commit()
db.close()
print("种子数据初始化完成！")
print("默认账号：admin/admin123 | reviewer/review123 | merchant/merchant123")
```

- [ ] **Step 4: Commit**

```bash
git add backend/alembic/ backend/alembic.ini backend/seed.py
git commit -m "feat: add alembic migrations and seed data"
```

---

## Phase 5: 前端基础设施

### Task 14: 前端项目脚手架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/env.d.ts`

- [ ] **Step 1: 创建 frontend/package.json**

```json
{
  "name": "health-product-merchant",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "axios": "^1.7.0",
    "element-plus": "^2.8.0",
    "@element-plus/icons-vue": "^2.3.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "vite": "^5.4.0",
    "@vitejs/plugin-vue": "^5.1.0",
    "vue-tsc": "^2.1.0",
    "@types/node": "^22.0.0"
  }
}
```

- [ ] **Step 2: 创建 frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/uploads': { target: 'http://127.0.0.1:8000', changeOrigin: true }
    }
  }
})
```

- [ ] **Step 3: 创建 frontend/index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>保健品商家后台管理系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 4: 创建 frontend/src/main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.mount('#app')
```

- [ ] **Step 5: 创建 frontend/src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 6: 创建 frontend/src/env.d.ts**

```typescript
/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: add frontend project scaffold"
```

---

### Task 15: 前端类型定义 + 工具函数 + API 层

**Files:**
- Create: `frontend/src/types/product.ts`
- Create: `frontend/src/types/qualification.ts`
- Create: `frontend/src/types/category.ts`
- Create: `frontend/src/types/audit.ts`
- Create: `frontend/src/utils/enums.ts`
- Create: `frontend/src/utils/validators.ts`
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/product.ts`
- Create: `frontend/src/api/qualification.ts`
- Create: `frontend/src/api/category.ts`
- Create: `frontend/src/api/audit.ts`

- [ ] **Step 1: 创建 frontend/src/types/product.ts**

```typescript
export interface ProductCompliance {
  approval_number: string
  main_ingredients: string
  efficacy_ingredients: string
  suitable_population: string
  unsuitable_population: string
  health_function: string
  usage_dosage: string
  shelf_life: string
  storage_method: string
  precautions: string
}

export interface ProductImage {
  id?: number
  image_type: 'main' | 'detail'
  file_url: string
  sort_order: number
}

export interface ProductCreate {
  category_id: number
  name: string
  brand: string
  spec: string
  price: number
  stock: number
  main_image: string
}

export interface ProductUpdate {
  category_id?: number
  name?: string
  brand?: string
  spec?: string
  price?: number
  stock?: number
  main_image?: string
  compliance?: ProductCompliance
}

export interface ProductListItem {
  id: number
  name: string
  brand: string
  category_name: string
  price: number
  stock: number
  main_image: string
  status: string
  submit_at: string | null
  created_at: string
}

export interface ProductDetail {
  id: number
  merchant_id: number
  category_id: number
  name: string
  brand: string
  spec: string
  price: number
  stock: number
  main_image: string
  status: string
  reject_reason: string | null
  submit_at: string | null
  audit_at: string | null
  audit_by: number | null
  version: number
  created_at: string
  updated_at: string
  compliance: ProductCompliance | null
  images: ProductImage[]
  detail: string | null
}

export interface DashboardStats {
  total_products: number
  pending_products: number
  approved_products: number
  rejected_products: number
  expiring_quals: number
  expired_quals: number
}
```

- [ ] **Step 2: 创建 frontend/src/types/qualification.ts**

```typescript
export interface QualificationInfo {
  id: number
  qual_type_id: number
  qual_type_name: string
  file_url: string
  file_name: string
  expire_date: string | null
  status: string
  remark: string
  created_at: string
}

export interface QualificationTypeInfo {
  id: number
  name: string
  code: string
  description: string
  is_required: boolean
  scope: string
  sort_order: number
}

export interface QualificationCreate {
  qual_type_id: number
  file_url: string
  file_name: string
  expire_date?: string | null
}
```

- [ ] **Step 3: 创建 frontend/src/types/category.ts**

```typescript
export interface CategoryInfo {
  id: number
  parent_id: number | null
  name: string
  description: string
  sort_order: number
  status: string
  children: CategoryInfo[]
}
```

- [ ] **Step 4: 创建 frontend/src/types/audit.ts**

```typescript
export interface AuditLogInfo {
  id: number
  reviewer_id: number
  action: string
  reason: string | null
  created_at: string
}

export interface VersionInfo {
  id: number
  version: number
  change_type: string
  changed_by: number
  remark: string
  created_at: string
}
```

- [ ] **Step 5: 创建 frontend/src/utils/enums.ts**

```typescript
export const ProductStatus = {
  draft: '草稿',
  pending_review: '待审核',
  approved: '已通过',
  rejected: '已驳回',
} as const

export const ProductStatusColor: Record<string, string> = {
  draft: 'info',
  pending_review: 'warning',
  approved: 'success',
  rejected: 'danger',
}

export const QualStatus = {
  valid: '有效',
  expiring: '即将到期',
  expired: '已过期',
} as const

export const QualStatusColor: Record<string, string> = {
  valid: 'success',
  expiring: 'warning',
  expired: 'danger',
}

export const ChangeType = {
  submit: '提交审核',
  approve: '审核通过',
  reject: '审核驳回',
  resubmit: '重新提交',
} as const
```

- [ ] **Step 6: 创建 frontend/src/utils/validators.ts**

```typescript
import type { FormItemRule } from 'element-plus'

export const required = (label: string): FormItemRule => ({
  required: true, message: `${label}不能为空`, trigger: 'blur'
})

export const maxLength = (max: number): FormItemRule => ({
  max, message: `不能超过${max}个字符`, trigger: 'blur'
})

export const positiveNumber: FormItemRule = {
  type: 'number', min: 0, message: '必须为正数', trigger: 'blur'
}

export const phoneRule: FormItemRule = {
  pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur'
}
```

- [ ] **Step 7: 创建 frontend/src/api/index.ts**

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => {
    const data = res.data
    if (data.code !== 200) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return data
  },
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    ElMessage.error(err.response?.data?.message || '网络错误')
    return Promise.reject(err)
  }
)

export default api
```

- [ ] **Step 8: 创建其他 API 文件**

`frontend/src/api/auth.ts`:
```typescript
import api from './index'
export const login = (data: { username: string; password: string }) => api.post('/auth/login', data)
export const logout = () => api.post('/auth/logout')
export const getMe = () => api.get('/auth/me')
```

`frontend/src/api/category.ts`:
```typescript
import api from './index'
export const getCategories = () => api.get('/categories')
export const getQualificationTypes = (scope?: string) => api.get('/qualification-types', { params: { scope } })
```

`frontend/src/api/product.ts`:
```typescript
import api from './index'
import type { ProductCreate, ProductUpdate } from '@/types/product'

export const getProducts = (params: Record<string, any>) => api.get('/merchant/products', { params })
export const createProduct = (data: ProductCreate) => api.post('/merchant/products', data)
export const getProduct = (id: number) => api.get(`/merchant/products/${id}`)
export const updateProduct = (id: number, data: ProductUpdate) => api.put(`/merchant/products/${id}`, data)
export const deleteProduct = (id: number) => api.delete(`/merchant/products/${id}`)
export const submitProduct = (id: number) => api.post(`/merchant/products/${id}/submit`)
export const getProductVersions = (id: number) => api.get(`/merchant/products/${id}/versions`)
export const getProductQualifications = (id: number) => api.get(`/merchant/products/${id}/qualifications`)
export const addProductQualification = (id: number, data: any) => api.post(`/merchant/products/${id}/qualifications`, data)
export const deleteProductQualification = (productId: number, qualId: number) => api.delete(`/merchant/products/${productId}/qualifications/${qualId}`)
export const uploadImage = (file: File) => {
  const fd = new FormData(); fd.append('file', file); return api.post('/upload/image', fd)
}
export const uploadFile = (file: File) => {
  const fd = new FormData(); fd.append('file', file); return api.post('/upload/file', fd)
}
export const getDashboard = () => api.get('/merchant/dashboard')
```

`frontend/src/api/qualification.ts`:
```typescript
import api from './index'
import type { QualificationCreate } from '@/types/qualification'

export const getMerchantQualifications = () => api.get('/merchant/qualifications')
export const createMerchantQualification = (data: QualificationCreate) => api.post('/merchant/qualifications', data)
export const updateMerchantQualification = (id: number, data: any) => api.put(`/merchant/qualifications/${id}`, data)
export const deleteMerchantQualification = (id: number) => api.delete(`/merchant/qualifications/${id}`)
```

`frontend/src/api/audit.ts`:
```typescript
import api from './index'

export const getReviewProducts = (params: Record<string, any>) => api.get('/reviewer/products', { params })
export const getReviewProduct = (id: number) => api.get(`/reviewer/products/${id}`)
export const approveProduct = (id: number) => api.post(`/reviewer/products/${id}/approve`)
export const rejectProduct = (id: number, reason: string) => api.post(`/reviewer/products/${id}/reject`, { reason })
export const batchApprove = (ids: number[]) => api.post('/reviewer/products/batch-approve', { ids })
export const batchReject = (ids: number[], reason: string) => api.post(`/reviewer/products/batch-reject?reason=${encodeURIComponent(reason)}`, { ids })
export const getReviewerDashboard = () => api.get('/reviewer/dashboard')
```

- [ ] **Step 9: Commit**

```bash
git add frontend/src/types/ frontend/src/utils/ frontend/src/api/
git commit -m "feat: add frontend types, utils, and API layer"
```

---

### Task 16: 前端路由 + 状态管理

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/router/routes/merchant.ts`
- Create: `frontend/src/router/routes/reviewer.ts`
- Create: `frontend/src/router/routes/admin.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/stores/product.ts`
- Create: `frontend/src/stores/review.ts`
- Create: `frontend/src/stores/category.ts`

- [ ] **Step 1: 创建路由文件**

`frontend/src/router/routes/merchant.ts`:
```typescript
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'

export const merchantRoutes: RouteRecordRaw[] = [
  {
    path: '/merchant',
    component: AppLayout,
    meta: { role: 'merchant' },
    children: [
      { path: 'dashboard', name: 'MerchantDashboard', component: () => import('@/views/merchant/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'products', name: 'MerchantProducts', component: () => import('@/views/merchant/ProductList.vue'), meta: { title: '商品管理' } },
      { path: 'products/create', name: 'ProductCreate', component: () => import('@/views/merchant/ProductCreate.vue'), meta: { title: '发布商品' } },
      { path: 'products/:id/edit', name: 'ProductEdit', component: () => import('@/views/merchant/ProductEdit.vue'), meta: { title: '编辑商品' } },
      { path: 'qualifications', name: 'MerchantQualifications', component: () => import('@/views/merchant/QualificationManage.vue'), meta: { title: '资质管理' } },
      { path: 'settings', name: 'MerchantSettings', component: () => import('@/views/merchant/Settings.vue'), meta: { title: '账号设置' } },
    ]
  }
]
```

`frontend/src/router/routes/reviewer.ts`:
```typescript
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'

export const reviewerRoutes: RouteRecordRaw[] = [
  {
    path: '/reviewer',
    component: AppLayout,
    meta: { role: 'reviewer' },
    children: [
      { path: 'dashboard', name: 'ReviewerDashboard', component: () => import('@/views/reviewer/Dashboard.vue'), meta: { title: '审核工作台' } },
      { path: 'products', name: 'ReviewerProducts', component: () => import('@/views/reviewer/ProductList.vue'), meta: { title: '审核列表' } },
      { path: 'products/:id', name: 'ReviewerProductAudit', component: () => import('@/views/reviewer/ProductAudit.vue'), meta: { title: '审核详情' }, props: true },
    ]
  }
]
```

`frontend/src/router/routes/admin.ts`:
```typescript
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/common/AppLayout.vue'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: AppLayout,
    meta: { role: 'admin' },
    children: [
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/CategoryManage.vue'), meta: { title: '品类管理' } },
      { path: 'merchants', name: 'AdminMerchants', component: () => import('@/views/admin/MerchantManage.vue'), meta: { title: '商家管理' } },
      { path: 'reviewers', name: 'AdminReviewers', component: () => import('@/views/admin/ReviewerManage.vue'), meta: { title: '审核员管理' } },
      { path: 'qualification-types', name: 'AdminQualTypes', component: () => import('@/views/admin/QualificationTypeManage.vue'), meta: { title: '资质类型管理' } },
    ]
  }
]
```

`frontend/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { merchantRoutes } from './routes/merchant'
import { reviewerRoutes } from './routes/reviewer'
import { adminRoutes } from './routes/admin'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: () => import('@/views/login/Login.vue'), meta: { title: '登录' } },
    ...merchantRoutes,
    ...reviewerRoutes,
    ...adminRoutes,
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')
  if (to.path !== '/login' && !token) {
    return next('/login')
  }
  if (to.meta.role && to.meta.role !== role) {
    return next('/login')
  }
  document.title = (to.meta.title as string) || '保健品商家后台'
  next()
})

export default router
```

- [ ] **Step 2: 创建 Pinia stores**

`frontend/src/stores/auth.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '')

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password })
    token.value = res.data.token
    role.value = res.data.role
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('role', res.data.role)
    localStorage.setItem('username', res.data.username)
    user.value = res.data
  }

  function logout() {
    token.value = ''
    role.value = ''
    user.value = null
    localStorage.clear()
  }

  return { user, token, role, login, logout }
})
```

`frontend/src/stores/product.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { updateProduct } from '@/api/product'
import type { ProductDetail, ProductCompliance } from '@/types/product'

export const useProductStore = defineStore('product', () => {
  const current = ref<Partial<ProductDetail>>({})
  const compliance = ref<ProductCompliance>({
    approval_number: '', main_ingredients: '', efficacy_ingredients: '',
    suitable_population: '', unsuitable_population: '', health_function: '',
    usage_dosage: '', shelf_life: '', storage_method: '', precautions: ''
  })

  let saveTimer: ReturnType<typeof setTimeout> | null = null

  function setCurrent(p: ProductDetail) {
    current.value = p
    if (p.compliance) compliance.value = p.compliance
  }

  function autoSave() {
    if (!current.value.id) return
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(async () => {
      try {
        await updateProduct(current.value.id!, {
          name: current.value.name,
          brand: current.value.brand,
          spec: current.value.spec,
          price: current.value.price,
          stock: current.value.stock,
          main_image: current.value.main_image,
          category_id: current.value.category_id,
          compliance: compliance.value,
        })
      } catch { /* silent save */ }
    }, 3000)
  }

  return { current, compliance, setCurrent, autoSave }
})
```

`frontend/src/stores/category.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCategories, getQualificationTypes } from '@/api/category'
import type { CategoryInfo, QualificationTypeInfo } from '@/types/category'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<CategoryInfo[]>([])
  const qualTypes = ref<QualificationTypeInfo[]>([])

  async function fetchCategories() { const res = await getCategories(); categories.value = res.data }
  async function fetchQualTypes(scope?: string) { const res = await getQualificationTypes(scope); qualTypes.value = res.data }

  return { categories, qualTypes, fetchCategories, fetchQualTypes }
})
```

`frontend/src/stores/review.ts`:
```typescript
import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { getReviewProducts, getReviewerDashboard } from '@/api/audit'
import type { ProductListItem } from '@/types/product'

export const useReviewStore = defineStore('review', () => {
  const list = ref<ProductListItem[]>([])
  const total = ref(0)
  const filter = reactive({ status: '', keyword: '', category_id: '', date_from: '', date_to: '', page: 1, page_size: 20 })
  const dashboard = ref({ pending_count: 0, approved_today: 0, rejected_today: 0 })

  async function fetchList() {
    const res = await getReviewProducts({ ...filter })
    list.value = res.data.list; total.value = res.data.total
  }

  async function fetchDashboard() { const res = await getReviewerDashboard(); dashboard.value = res.data }

  return { list, total, filter, dashboard, fetchList, fetchDashboard }
})
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/ frontend/src/stores/
git commit -m "feat: add router, guards, and Pinia stores"
```

---

## Phase 6: 前端组件

### Task 17: 通用组件

**Files:**
- Create: `frontend/src/components/common/AppLayout.vue`
- Create: `frontend/src/components/common/StatusTag.vue`
- Create: `frontend/src/components/common/UploadImage.vue`
- Create: `frontend/src/components/common/UploadFile.vue`
- Create: `frontend/src/components/common/SearchForm.vue`
- Create: `frontend/src/components/common/PaginationTable.vue`

- [ ] **Step 1: 创建 AppLayout.vue**

```vue
<template>
  <el-container class="layout">
    <el-aside width="220px">
      <div class="logo">保健品商家后台</div>
      <el-menu :default-active="route.path" router>
        <template v-for="item in menuItems" :key="item.path">
          <el-sub-menu v-if="item.children" :index="item.path">
            <template #title>{{ item.title }}</template>
            <el-menu-item v-for="child in item.children" :key="child.path" :index="child.path">{{ child.title }}</el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="item.path">{{ item.title }}</el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <span>{{ route.meta.title }}</span>
        <el-dropdown @command="handleCommand">
          <span class="user">{{ username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const username = localStorage.getItem('username') || ''

const role = localStorage.getItem('role')

const menuItems = computed(() => {
  if (role === 'merchant') return [
    { path: '/merchant/dashboard', title: '工作台' },
    { path: '/merchant/products', title: '商品管理' },
    { path: '/merchant/qualifications', title: '资质管理' },
    { path: '/merchant/settings', title: '账号设置' },
  ]
  if (role === 'reviewer') return [
    { path: '/reviewer/dashboard', title: '审核工作台' },
    { path: '/reviewer/products', title: '审核列表' },
  ]
  if (role === 'admin') return [
    { path: '/admin/categories', title: '品类管理' },
    { path: '/admin/merchants', title: '商家管理' },
    { path: '/admin/reviewers', title: '审核员管理' },
    { path: '/admin/qualification-types', title: '资质类型管理' },
  ]
  return []
})

function handleCommand(cmd: string) {
  if (cmd === 'logout') { auth.logout(); router.push('/login') }
}
</script>

<style scoped>
.layout { min-height: 100vh; }
.logo { padding: 16px 20px; font-size: 16px; font-weight: bold; color: #fff; background: #001529; }
.el-aside { background: #001529; }
.el-header { display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid #e8e8e8; padding: 0 20px; }
.user { cursor: pointer; }
</style>
```

- [ ] **Step 2: 创建 StatusTag.vue**

```vue
<template>
  <el-tag :type="color" size="small">{{ text }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ProductStatus, ProductStatusColor, QualStatus, QualStatusColor } from '@/utils/enums'

const props = defineProps<{ status: string; type?: 'product' | 'qual' }>()

const text = computed(() => props.type === 'qual' ? (QualStatus as any)[props.status] || props.status : (ProductStatus as any)[props.status] || props.status)
const color = computed(() => props.type === 'qual' ? (QualStatusColor as any)[props.status] || 'info' : (ProductStatusColor as any)[props.status] || 'info')
</script>
```

- [ ] **Step 3: 创建 UploadImage.vue**

```vue
<template>
  <el-upload :http-request="customUpload" list-type="picture-card" :file-list="fileList"
             :on-preview="onPreview" :on-remove="onRemove" :limit="limit" :multiple="limit > 1">
    <el-icon><Plus /></el-icon>
  </el-upload>
  <el-dialog v-model="previewVisible" title="预览">
    <img :src="previewUrl" style="width:100%" />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { uploadImage } from '@/api/product'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps<{ modelValue: string[]; limit?: number }>()
const emit = defineEmits(['update:modelValue'])

const fileList = ref<any[]>([])
const previewVisible = ref(false)
const previewUrl = ref('')

watch(() => props.modelValue, (v) => {
  fileList.value = (v || []).map((url, i) => ({ uid: i, name: `image-${i}`, url, status: 'success' }))
}, { immediate: true })

async function customUpload(opts: any) {
  const res = await uploadImage(opts.file)
  const url = res.data.url
  const urls = [...(props.modelValue || []), url]
  emit('update:modelValue', urls)
}

function onPreview(file: any) { previewUrl.value = file.url; previewVisible.value = true }
function onRemove(_file: any, files: any[]) {
  const urls = files.map((f: any) => f.url)
  emit('update:modelValue', urls)
}
</script>
```

- [ ] **Step 4: 创建 UploadFile.vue**

```vue
<template>
  <el-upload :http-request="customUpload" :file-list="fileList" :on-remove="onRemove" :limit="1"
             :on-change="onChange" :auto-upload="false" drag>
    <el-icon><UploadFilled /></el-icon>
    <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
    <template #tip><div class="el-upload__tip">支持 JPG/PNG/PDF，不超过 10MB</div></template>
  </el-upload>
  <el-input v-if="fileList.length && showExpire" v-model="expireDate" type="date" placeholder="到期日期" style="width:200px;margin-top:8px" />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { uploadFile } from '@/api/product'
import { UploadFilled } from '@element-plus/icons-vue'

const props = defineProps<{ modelValue: string; modelFileName?: string; showExpire?: boolean; expireModelValue?: string }>()
const emit = defineEmits(['update:modelValue', 'update:modelFileName', 'update:expireModelValue'])

const fileList = ref<any[]>([])
const expireDate = ref(props.expireModelValue || '')

watch(() => props.modelValue, (v) => {
  if (v) fileList.value = [{ uid: 0, name: props.modelFileName || 'file', url: v, status: 'success' }]
  else fileList.value = []
}, { immediate: true })

watch(expireDate, (v) => emit('update:expireModelValue', v))

async function customUpload(opts: any) {
  const res = await uploadFile(opts.file)
  emit('update:modelValue', res.data.url)
  emit('update:modelFileName', res.data.name)
}

function onChange(_file: any, files: any[]) { if (files.length) customUpload({ file: files[0].raw }) }
function onRemove() { emit('update:modelValue', ''); emit('update:modelFileName', '') }
</script>
```

- [ ] **Step 5: 创建 PaginationTable.vue**

```vue
<template>
  <div>
    <el-table :data="data" border stripe v-loading="loading" style="width:100%">
      <slot />
    </el-table>
    <el-pagination v-if="showPagination" :current-page="page" :page-size="pageSize" :total="total"
                   :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next, jumper"
                   @size-change="$emit('sizeChange', $event)" @current-change="$emit('pageChange', $event)"
                   style="margin-top:16px;justify-content:flex-end" />
  </div>
</template>

<script setup lang="ts">
defineProps<{ data: any[]; loading?: boolean; total?: number; page?: number; pageSize?: number; showPagination?: boolean }>()
defineEmits(['sizeChange', 'pageChange'])
</script>
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/common/
git commit -m "feat: add common components (layout, status, uploads, table)"
```

---

### Task 18: 商品相关组件

**Files:**
- Create: `frontend/src/components/product/ProductBasicForm.vue`
- Create: `frontend/src/components/product/ProductComplianceForm.vue`
- Create: `frontend/src/components/product/ProductMediaForm.vue`
- Create: `frontend/src/components/product/ProductQualificationForm.vue`
- Create: `frontend/src/components/product/ProductPreview.vue`
- Create: `frontend/src/components/qualification/QualificationCard.vue`
- Create: `frontend/src/components/audit/AuditActionPanel.vue`
- Create: `frontend/src/components/audit/VersionHistory.vue`

- [ ] **Step 1: 创建 ProductBasicForm.vue**

```vue
<template>
  <el-form :model="form" :rules="rules" label-width="100px">
    <el-form-item label="商品名称" prop="name"><el-input v-model="form.name" maxlength="200" /></el-form-item>
    <el-row>
      <el-col :span="12"><el-form-item label="品类" prop="category_id">
        <el-cascader v-model="categoryValue" :options="catOptions" :props="{ value:'id', label:'name', checkStrictly:true }" placeholder="选择品类" @change="onCatChange" />
      </el-form-item></el-col>
      <el-col :span="12"><el-form-item label="品牌" prop="brand"><el-input v-model="form.brand" /></el-form-item></el-col>
    </el-row>
    <el-row>
      <el-col :span="12"><el-form-item label="规格" prop="spec"><el-input v-model="form.spec" placeholder="如 60粒/瓶" /></el-form-item></el-col>
      <el-col :span="6"><el-form-item label="价格(元)" prop="price"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item></el-col>
      <el-col :span="6"><el-form-item label="库存" prop="stock"><el-input-number v-model="form.stock" :min="0" /></el-form-item></el-col>
    </el-row>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCategoryStore } from '@/stores/category'
import { required } from '@/utils/validators'

const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])
const store = useCategoryStore()

const form = ref({ ...props.modelValue })
const categoryValue = ref<any[]>([])

const catOptions = computed(() => store.categories.map(c => ({
  id: c.id, name: c.name, children: c.children?.map(s => ({ id: s.id, name: s.name })) || []
})))

watch(form, (v) => emit('update:modelValue', { ...v }), { deep: true })

function onCatChange(vals: any[]) {
  form.value.category_id = vals[vals.length - 1] || 0
  emit('update:modelValue', { ...form.value })
}

const rules = {
  name: [required('商品名称')],
  category_id: [required('品类')],
}
</script>
```

- [ ] **Step 2: 创建 ProductComplianceForm.vue**

```vue
<template>
  <el-form :model="form" label-width="140px">
    <el-form-item label="批准文号（蓝帽）" prop="approval_number">
      <el-input v-model="form.approval_number" placeholder="国食健字Gxxxxxx" />
    </el-form-item>
    <el-form-item label="主要原料"><el-input v-model="form.main_ingredients" type="textarea" :rows="2" /></el-form-item>
    <el-form-item label="功效成分及含量"><el-input v-model="form.efficacy_ingredients" type="textarea" :rows="2" /></el-form-item>
    <el-row>
      <el-col :span="12"><el-form-item label="适宜人群"><el-input v-model="form.suitable_population" /></el-form-item></el-col>
      <el-col :span="12"><el-form-item label="不适宜人群"><el-input v-model="form.unsuitable_population" /></el-form-item></el-col>
    </el-row>
    <el-form-item label="保健功能"><el-input v-model="form.health_function" /></el-form-item>
    <el-form-item label="食用方法及用量"><el-input v-model="form.usage_dosage" /></el-form-item>
    <el-row>
      <el-col :span="12"><el-form-item label="保质期"><el-input v-model="form.shelf_life" placeholder="如 24个月" /></el-form-item></el-col>
      <el-col :span="12"><el-form-item label="贮藏方法"><el-input v-model="form.storage_method" /></el-form-item></el-col>
    </el-row>
    <el-form-item label="注意事项"><el-input v-model="form.precautions" type="textarea" :rows="2" /></el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ modelValue: any }>()
const emit = defineEmits(['update:modelValue'])
const form = ref({ ...props.modelValue })
watch(form, (v) => emit('update:modelValue', { ...v }), { deep: true })
</script>
```

- [ ] **Step 3: 创建 ProductMediaForm.vue** (图片上传 + 详情)

```vue
<template>
  <div>
    <h4>商品主图</h4>
    <UploadImage v-model="mainImages" :limit="1" />
    <h4 style="margin-top:16px">详情图片</h4>
    <UploadImage v-model="detailImages" :limit="10" />
    <h4 style="margin-top:16px">商品详情描述</h4>
    <el-input v-model="detail" type="textarea" :rows="8" placeholder="商品详情描述（支持富文本）" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import UploadImage from '@/components/common/UploadImage.vue'

const props = defineProps<{ modelValue: { main_images: string[]; detail_images: string[]; detail: string } }>()
const emit = defineEmits(['update:modelValue'])

const mainImages = ref(props.modelValue?.main_images || [])
const detailImages = ref(props.modelValue?.detail_images || [])
const detail = ref(props.modelValue?.detail || '')

watch([mainImages, detailImages, detail], () => {
  emit('update:modelValue', { main_images: mainImages.value, detail_images: detailImages.value, detail: detail.value })
}, { deep: true })
</script>
```

- [ ] **Step 4: 创建 ProductQualificationForm.vue**

```vue
<template>
  <div>
    <h4>商品资质</h4>
    <div v-for="qt in productQualTypes" :key="qt.id" style="margin-bottom:16px">
      <el-form-item :label="qt.name" :required="qt.is_required">
        <UploadFile :model-value="getQualFile(qt.id)" :model-file-name="getQualName(qt.id)"
                    :show-expire="true" :expire-model-value="getQualExpire(qt.id)"
                    @update:model-value="(v: string) => setQualFile(qt.id, v)"
                    @update:model-file-name="(v: string) => setQualName(qt.id, v)"
                    @update:expire-model-value="(v: string) => setQualExpire(qt.id, v)" />
      </el-form-item>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import UploadFile from '@/components/common/UploadFile.vue'
import { getQualificationTypes } from '@/api/category'

const props = defineProps<{ modelValue: Record<number, { file_url: string; file_name: string; expire_date: string }> }>()
const emit = defineEmits(['update:modelValue'])
const productQualTypes = ref<any[]>([])

const qualData = ref<Record<number, any>>({ ...props.modelValue })

onMounted(async () => {
  const res = await getQualificationTypes('product')
  productQualTypes.value = res.data
})

function getQualFile(id: number) { return qualData.value[id]?.file_url || '' }
function getQualName(id: number) { return qualData.value[id]?.file_name || '' }
function getQualExpire(id: number) { return qualData.value[id]?.expire_date || '' }
function setQualFile(id: number, v: string) { if (!qualData.value[id]) qualData.value[id] = {}; qualData.value[id].file_url = v; emit('update:modelValue', { ...qualData.value }) }
function setQualName(id: number, v: string) { if (!qualData.value[id]) qualData.value[id] = {}; qualData.value[id].file_name = v; emit('update:modelValue', { ...qualData.value }) }
function setQualExpire(id: number, v: string) { if (!qualData.value[id]) qualData.value[id] = {}; qualData.value[id].expire_date = v; emit('update:modelValue', { ...qualData.value }) }
</script>
```

- [ ] **Step 5: 创建 ProductPreview.vue**

```vue
<template>
  <el-descriptions title="商品信息预览" :column="2" border>
    <el-descriptions-item label="商品名称">{{ data.name }}</el-descriptions-item>
    <el-descriptions-item label="品牌">{{ data.brand }}</el-descriptions-item>
    <el-descriptions-item label="规格">{{ data.spec }}</el-descriptions-item>
    <el-descriptions-item label="价格">¥{{ data.price }}</el-descriptions-item>
    <el-descriptions-item label="库存">{{ data.stock }}</el-descriptions-item>
    <el-descriptions-item label="批准文号">{{ data.compliance?.approval_number }}</el-descriptions-item>
  </el-descriptions>
</template>

<script setup lang="ts">
defineProps<{ data: any }>()
</script>
```

- [ ] **Step 6: 创建 QualificationCard.vue**

```vue
<template>
  <el-card>
    <template #header><span>{{ qual.qual_type_name || `资质 #${qual.qual_type_id}` }}</span><StatusTag :status="qual.status" type="qual" style="margin-left:8px" /></template>
    <div><a :href="qual.file_url" target="_blank">{{ qual.file_name }}</a></div>
    <div v-if="qual.expire_date">到期日期: {{ qual.expire_date }}</div>
    <slot />
  </el-card>
</template>

<script setup lang="ts">
import StatusTag from '@/components/common/StatusTag.vue'
defineProps<{ qual: any }>()
</script>
```

- [ ] **Step 7: 创建 AuditActionPanel.vue**

```vue
<template>
  <div>
    <el-button type="success" size="large" @click="$emit('approve')">审核通过</el-button>
    <el-popconfirm title="确定驳回该商品？" @confirm="confirmReject">
      <template #reference><el-button type="danger" size="large" style="margin-left:16px">驳回</el-button></template>
      <el-input v-model="reason" placeholder="请输入驳回原因（必填）" style="width:300px;margin-top:8px" />
    </el-popconfirm>
    <div v-if="reasonError" style="color:red;margin-top:8px">请填写驳回原因</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['approve', 'reject'])
const reason = ref('')
const reasonError = ref(false)

function confirmReject() {
  if (!reason.value.trim()) { reasonError.value = true; return }
  reasonError.value = false
  emit('reject', reason.value)
}
</script>
```

- [ ] **Step 8: 创建 VersionHistory.vue** — 版本时间线

```vue
<template>
  <el-timeline>
    <el-timeline-item v-for="v in versions" :key="v.id" :timestamp="v.created_at" placement="top">
      <el-tag>{{ changeTypeText(v.change_type) }}</el-tag>
      <span v-if="v.remark" style="margin-left:8px;color:#999">{{ v.remark }}</span>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup lang="ts">
import { ChangeType } from '@/utils/enums'
defineProps<{ versions: any[] }>()
function changeTypeText(t: string) { return (ChangeType as any)[t] || t }
</script>
```

- [ ] **Step 9: Commit**

```bash
git add frontend/src/components/product/ frontend/src/components/qualification/ frontend/src/components/audit/
git commit -m "feat: add product form, qualification, audit components"
```

---

### Task 19: 页面 — 登录 + 商家端

**Files:**
- Create: `frontend/src/views/login/Login.vue`
- Create: `frontend/src/views/merchant/Dashboard.vue`
- Create: `frontend/src/views/merchant/ProductList.vue`
- Create: `frontend/src/views/merchant/ProductCreate.vue`
- Create: `frontend/src/views/merchant/ProductEdit.vue`
- Create: `frontend/src/views/merchant/QualificationManage.vue`
- Create: `frontend/src/views/merchant/Settings.vue`

- [ ] **Step 1: 创建 Login.vue**

```vue
<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>保健品商家后台管理系统</h2>
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item prop="username"><el-input v-model="form.username" placeholder="用户名" /></el-form-item>
        <el-form-item prop="password"><el-input v-model="form.password" type="password" placeholder="密码" show-password /></el-form-item>
        <el-form-item><el-button type="primary" :loading="loading" @click="doLogin" style="width:100%">登录</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function doLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    const role = auth.role
    if (role === 'merchant') router.push('/merchant/dashboard')
    else if (role === 'reviewer') router.push('/reviewer/dashboard')
    else if (role === 'admin') router.push('/admin/categories')
  } catch (e: any) {
    ElMessage.error(e.message || '登录失败')
  } finally { loading.value = false }
}
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; background: #f0f2f5; }
.login-card { width: 400px; }
.login-card h2 { text-align: center; margin-bottom: 24px; }
</style>
```

- [ ] **Step 2: 创建 Dashboard.vue** (商家工作台)

```vue
<template>
  <div>
    <el-row :gutter="16">
      <el-col :span="6"><el-statistic title="全部商品" :value="stats.total_products" /></el-col>
      <el-col :span="6"><el-statistic title="待审核" :value="stats.pending_products" /></el-col>
      <el-col :span="6"><el-statistic title="已通过" :value="stats.approved_products" /></el-col>
      <el-col :span="6"><el-statistic title="已驳回" :value="stats.rejected_products" /></el-col>
    </el-row>
    <el-divider />
    <h3>资质到期提醒</h3>
    <el-row :gutter="16">
      <el-col :span="8"><el-statistic title="即将到期" :value="stats.expiring_quals">
        <template #suffix><el-tag type="warning" size="small">需关注</el-tag></template>
      </el-statistic></el-col>
      <el-col :span="8"><el-statistic title="已过期" :value="stats.expired_quals">
        <template #suffix><el-tag type="danger" size="small">立即更新</el-tag></template>
      </el-statistic></el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDashboard } from '@/api/product'

const stats = ref({ total_products: 0, pending_products: 0, approved_products: 0, rejected_products: 0, expiring_quals: 0, expired_quals: 0 })

onMounted(async () => { const res = await getDashboard(); stats.value = res.data })
</script>
```

- [ ] **Step 3: 创建 ProductList.vue**

```vue
<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:16px">
      <div>
        <el-select v-model="filter.status" placeholder="状态筛选" clearable style="width:140px" @change="fetchData">
          <el-option v-for="(label, key) in ProductStatus" :key="key" :label="label" :value="key" />
        </el-select>
        <el-input v-model="filter.keyword" placeholder="搜索商品名称" clearable style="width:200px;margin-left:8px" @input="fetchData" />
      </div>
      <el-button type="primary" @click="$router.push('/merchant/products/create')">发布商品</el-button>
    </div>
    <PaginationTable :data="list" :total="total" :page="filter.page" :page-size="filter.page_size" :loading="loading"
                     @page-change="(p:number)=>{filter.page=p;fetchData()}" @size-change="(s:number)=>{filter.page_size=s;fetchData()}">
      <el-table-column prop="name" label="商品名称" />
      <el-table-column prop="brand" label="品牌" width="120" />
      <el-table-column label="价格" width="100"><template #default="{row}">¥{{ row.price }}</template></el-table-column>
      <el-table-column prop="stock" label="库存" width="80" />
      <el-table-column label="状态" width="100"><template #default="{row}"><StatusTag :status="row.status" /></template></el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{row}">
          <el-button size="small" @click="$router.push(`/merchant/products/${row.id}/edit`)">编辑</el-button>
          <el-button v-if="row.status==='draft'" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </PaginationTable>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getProducts, deleteProduct } from '@/api/product'
import PaginationTable from '@/components/common/PaginationTable.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { ProductStatus } from '@/utils/enums'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const filter = reactive({ status: '', keyword: '', page: 1, page_size: 20 })

async function fetchData() { loading.value = true; try { const res = await getProducts({ ...filter }); list.value = res.data.list; total.value = res.data.total } finally { loading.value = false } }

async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  await deleteProduct(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(fetchData)
</script>
```

- [ ] **Step 4: 创建 ProductCreate.vue** — 分步表单

```vue
<template>
  <div>
    <el-steps :active="step" align-center style="margin-bottom:24px">
      <el-step title="基本信息" /><el-step title="合规信息" /><el-step title="图片详情" /><el-step title="商品资质" /><el-step title="预览提交" />
    </el-steps>
    <ProductBasicForm v-if="step===0" v-model="basic" />
    <ProductComplianceForm v-if="step===1" v-model="compliance" />
    <ProductMediaForm v-if="step===2" v-model="media" />
    <ProductQualificationForm v-if="step===3" v-model="qualifications" />
    <ProductPreview v-if="step===4" :data="previewData" />
    <div style="text-align:center;margin-top:24px">
      <el-button v-if="step>0" @click="step--">上一步</el-button>
      <el-button v-if="step<4" type="primary" @click="nextStep">下一步</el-button>
      <el-button v-if="step===4" type="success" @click="submit">确认提交</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProductBasicForm from '@/components/product/ProductBasicForm.vue'
import ProductComplianceForm from '@/components/product/ProductComplianceForm.vue'
import ProductMediaForm from '@/components/product/ProductMediaForm.vue'
import ProductQualificationForm from '@/components/product/ProductQualificationForm.vue'
import ProductPreview from '@/components/product/ProductPreview.vue'
import { createProduct, updateProduct, submitProduct, addProductQualification } from '@/api/product'
import { useCategoryStore } from '@/stores/category'

const router = useRouter()
const step = ref(0)
const productId = ref(0)
const basic = ref({ name: '', brand: '', spec: '', category_id: 0, price: 0, stock: 0, main_image: '' })
const compliance = ref({})
const media = ref({ main_images: [] as string[], detail_images: [] as string[], detail: '' })
const qualifications = ref<Record<number, any>>({})

const store = useCategoryStore()

onMounted(async () => { await store.fetchCategories(); await store.fetchQualTypes('product') })

const previewData = computed(() => ({ ...basic.value, compliance: compliance.value }))

async function nextStep() {
  if (step.value === 0 && !productId.value) {
    const res = await createProduct(basic.value)
    productId.value = res.data.id
  }
  step.value++
}

async function submit() {
  try {
    await updateProduct(productId.value, { compliance: compliance.value, main_image: basic.value.main_image })

    for (const [typeId, data] of Object.entries(qualifications.value)) {
      if (data.file_url) {
        await addProductQualification(productId.value, {
          qual_type_id: Number(typeId), file_url: data.file_url, file_name: data.file_name, expire_date: data.expire_date || null
        })
      }
    }

    await submitProduct(productId.value)
    ElMessage.success('提交审核成功')
    router.push('/merchant/products')
  } catch (e: any) {
    ElMessage.error(e.message || '提交失败')
  }
}
</script>
```

- [ ] **Step 5: 创建 ProductEdit.vue**

```vue
<template>
  <div>
    <h3>编辑商品</h3>
    <el-tabs v-model="tab">
      <el-tab-pane label="基本信息" name="basic">
        <ProductBasicForm v-model="form" />
      </el-tab-pane>
      <el-tab-pane label="合规信息" name="compliance">
        <ProductComplianceForm v-model="compliance" />
      </el-tab-pane>
      <el-tab-pane label="图片详情" name="media">
        <ProductMediaForm v-model="media" />
      </el-tab-pane>
      <el-tab-pane label="商品资质" name="quals">
        <ProductQualificationForm v-model="qualifications" />
      </el-tab-pane>
      <el-tab-pane label="版本历史" name="versions">
        <VersionHistory v-if="versions.length" :versions="versions" />
        <el-empty v-else description="暂无版本记录" />
      </el-tab-pane>
    </el-tabs>
    <div style="text-align:center;margin-top:16px">
      <el-button type="primary" @click="save">保存草稿</el-button>
      <el-button type="success" @click="submit">提交审核</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProductBasicForm from '@/components/product/ProductBasicForm.vue'
import ProductComplianceForm from '@/components/product/ProductComplianceForm.vue'
import ProductMediaForm from '@/components/product/ProductMediaForm.vue'
import ProductQualificationForm from '@/components/product/ProductQualificationForm.vue'
import VersionHistory from '@/components/audit/VersionHistory.vue'
import { getProduct, updateProduct, submitProduct, getProductVersions } from '@/api/product'
import { useCategoryStore } from '@/stores/category'

const route = useRoute()
const router = useRouter()
const tab = ref('basic')
const id = Number(route.params.id)
const form = ref({ name: '', brand: '', spec: '', category_id: 0, price: 0, stock: 0, main_image: '' })
const compliance = ref({})
const media = ref({ main_images: [], detail_images: [], detail: '' })
const qualifications = ref<Record<number, any>>({})
const versions = ref<any[]>([])

const store = useCategoryStore()

onMounted(async () => {
  await store.fetchCategories()
  await store.fetchQualTypes('product')
  const res = await getProduct(id)
  const p = res.data
  form.value = { name: p.name, brand: p.brand, spec: p.spec, category_id: p.category_id, price: p.price, stock: p.stock, main_image: p.main_image }
  compliance.value = p.compliance || {}
  media.value = { main_images: p.images?.filter((i: any) => i.image_type === 'main').map((i: any) => i.file_url) || [],
                  detail_images: p.images?.filter((i: any) => i.image_type === 'detail').map((i: any) => i.file_url) || [],
                  detail: p.detail || '' }
  try { const v = await getProductVersions(id); versions.value = v.data } catch {}
})

async function save() {
  await updateProduct(id, { ...form.value, compliance: compliance.value })
  ElMessage.success('保存成功')
}

async function submit() {
  await save()
  await submitProduct(id)
  ElMessage.success('提交审核成功')
  router.push('/merchant/products')
}
</script>
```

- [ ] **Step 6: 创建 QualificationManage.vue** (商家资质管理)

```vue
<template>
  <div>
    <h3>商家资质管理</h3>
    <el-button type="primary" @click="showUpload=true" style="margin-bottom:16px">上传资质</el-button>
    <el-row :gutter="16">
      <el-col v-for="qt in merchantQualTypes" :key="qt.id" :span="8" style="margin-bottom:16px">
        <el-card>
          <template #header><span>{{ qt.name }}</span><el-tag v-if="qt.is_required" type="danger" size="small" style="margin-left:8px">必传</el-tag></template>
          <template v-if="getQual(qt.id)">
            <div><a :href="getQual(qt.id).file_url" target="_blank">{{ getQual(qt.id).file_name }}</a></div>
            <div v-if="getQual(qt.id).expire_date">到期: {{ getQual(qt.id).expire_date }}</div>
            <StatusTag :status="getQual(qt.id).status" type="qual" />
            <el-button size="small" type="danger" @click="deleteQual(getQual(qt.id).id)">删除</el-button>
          </template>
          <el-upload v-else :http-request="(opts:any) => doUpload(qt.id, opts)" drag :limit="1">
            <el-icon><UploadFilled /></el-icon>
            <div>点击或拖拽上传</div>
          </el-upload>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMerchantQualifications, createMerchantQualification, deleteMerchantQualification } from '@/api/qualification'
import { getQualificationTypes } from '@/api/category'
import { uploadFile } from '@/api/product'
import StatusTag from '@/components/common/StatusTag.vue'
import { UploadFilled } from '@element-plus/icons-vue'

const merchantQualTypes = ref<any[]>([])
const quals = ref<any[]>([])
const showUpload = ref(false)

onMounted(async () => {
  const [typesRes, qualsRes] = await Promise.all([getQualificationTypes('merchant'), getMerchantQualifications()])
  merchantQualTypes.value = typesRes.data
  quals.value = qualsRes.data
})

function getQual(typeId: number) { return quals.value.find((q: any) => q.qual_type_id === typeId) }

async function doUpload(typeId: number, opts: any) {
  const fileRes = await uploadFile(opts.file)
  await createMerchantQualification({ qual_type_id: typeId, file_url: fileRes.data.url, file_name: fileRes.data.name })
  const qualsRes = await getMerchantQualifications(); quals.value = qualsRes.data
  ElMessage.success('上传成功')
}

async function deleteQual(qualId: number) {
  await deleteMerchantQualification(qualId)
  const res = await getMerchantQualifications(); quals.value = res.data
  ElMessage.success('删除成功')
}
</script>
```

- [ ] **Step 7: 创建 Settings.vue** (账号设置)

```vue
<template>
  <el-card>
    <el-descriptions title="账号信息" :column="1" border>
      <el-descriptions-item label="用户名">{{ username }}</el-descriptions-item>
      <el-descriptions-item label="角色">商家</el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup lang="ts">
const username = localStorage.getItem('username') || ''
</script>
```

- [ ] **Step 8: Commit**

```bash
git add frontend/src/views/login/ frontend/src/views/merchant/
git commit -m "feat: add login page and merchant pages"
```

---

### Task 20: 页面 — 审核员端 + 超管端

**Files:**
- Create: `frontend/src/views/reviewer/Dashboard.vue`
- Create: `frontend/src/views/reviewer/ProductList.vue`
- Create: `frontend/src/views/reviewer/ProductAudit.vue`
- Create: `frontend/src/views/admin/CategoryManage.vue`
- Create: `frontend/src/views/admin/MerchantManage.vue`
- Create: `frontend/src/views/admin/QualificationTypeManage.vue`
- Create: `frontend/src/views/admin/ReviewerManage.vue`

- [ ] **Step 1: 创建 reviewer/Dashboard.vue**

```vue
<template>
  <el-row :gutter="16">
    <el-col :span="8"><el-statistic title="待审核商品" :value="dashboard.pending_count" /></el-col>
    <el-col :span="8"><el-statistic title="今日通过" :value="dashboard.approved_today" /></el-col>
    <el-col :span="8"><el-statistic title="今日驳回" :value="dashboard.rejected_today" /></el-col>
  </el-row>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useReviewStore } from '@/stores/review'
const store = useReviewStore()
onMounted(() => store.fetchDashboard())
const dashboard = store.dashboard
</script>
```

- [ ] **Step 2: 创建 reviewer/ProductList.vue** — 审核列表

```vue
<template>
  <div>
    <div style="display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap">
      <el-select v-model="filter.status" placeholder="状态" clearable @change="fetch" style="width:120px">
        <el-option label="待审核" value="pending_review" /><el-option label="已通过" value="approved" /><el-option label="已驳回" value="rejected" />
      </el-select>
      <el-input v-model="filter.keyword" placeholder="搜索商品" clearable @input="fetch" style="width:180px" />
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="提交开始" end-placeholder="提交结束" @change="onDateChange" />
      <el-button type="success" @click="batchApprove">批量通过</el-button>
      <el-button type="danger" @click="batchReject">批量驳回</el-button>
    </div>
    <PaginationTable :data="list" :total="total" :page="filter.page" :page_size="filter.page_size" :loading="loading"
                     @page-change="(p:number)=>{filter.page=p;fetch()}" @size-change="(s:number)=>{filter.page_size=s;fetch()}">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="name" label="商品名称" />
      <el-table-column prop="brand" label="品牌" width="100" />
      <el-table-column label="价格" width="80"><template #default="{row}">¥{{ row.price }}</template></el-table-column>
      <el-table-column label="状态" width="80"><template #default="{row}"><StatusTag :status="row.status" /></template></el-table-column>
      <el-table-column label="提交时间" width="160"><template #default="{row}">{{ row.submit_at }}</template></el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{row}"><el-button size="small" @click="$router.push(`/reviewer/products/${row.id}`)">审核</el-button></template>
      </el-table-column>
    </PaginationTable>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useReviewStore } from '@/stores/review'
import PaginationTable from '@/components/common/PaginationTable.vue'
import StatusTag from '@/components/common/StatusTag.vue'

const store = useReviewStore()
const { list, total, filter, fetchList } = store
const loading = ref(false)
const dateRange = ref<any[]>([])

function onDateChange(vals: any[]) {
  filter.date_from = vals?.[0]?.toISOString().slice(0, 10) || ''
  filter.date_to = vals?.[1]?.toISOString().slice(0, 10) || ''
  fetch()
}

async function fetch() { loading.value = true; try { await fetchList() } finally { loading.value = false } }
onMounted(fetch)
</script>
```

- [ ] **Step 3: 创建 reviewer/ProductAudit.vue**

```vue
<template>
  <div>
    <h3>商品审核</h3>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="商品名称">{{ product.name }}</el-descriptions-item>
      <el-descriptions-item label="品牌">{{ product.brand }}</el-descriptions-item>
      <el-descriptions-item label="规格">{{ product.spec }}</el-descriptions-item>
      <el-descriptions-item label="价格">¥{{ product.price }}</el-descriptions-item>
      <el-descriptions-item label="库存">{{ product.stock }}</el-descriptions-item>
      <el-descriptions-item label="批准文号">{{ product.compliance?.approval_number }}</el-descriptions-item>
      <el-descriptions-item label="主要原料" :span="2">{{ product.compliance?.main_ingredients }}</el-descriptions-item>
      <el-descriptions-item label="适宜人群">{{ product.compliance?.suitable_population }}</el-descriptions-item>
      <el-descriptions-item label="不适宜人群">{{ product.compliance?.unsuitable_population }}</el-descriptions-item>
      <el-descriptions-item label="保健功能" :span="2">{{ product.compliance?.health_function }}</el-descriptions-item>
      <el-descriptions-item label="详情描述" :span="2">{{ product.detail }}</el-descriptions-item>
    </el-descriptions>
    <div v-if="product.images?.length" style="margin-top:16px">
      <h4>商品图片</h4>
      <el-image v-for="img in product.images" :key="img.id" :src="img.file_url" style="width:120px;height:120px;margin-right:8px" />
    </div>
    <div style="margin-top:16px">
      <AuditActionPanel v-if="product.status==='pending_review'" @approve="doApprove" @reject="doReject" />
      <el-tag v-else :type="product.status === 'approved' ? 'success' : 'danger'">{{ product.status === 'approved' ? '已通过' : '已驳回' }}</el-tag>
      <div v-if="product.reject_reason" style="margin-top:8px;color:red">驳回原因: {{ product.reject_reason }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReviewProduct, approveProduct, rejectProduct } from '@/api/audit'
import AuditActionPanel from '@/components/audit/AuditActionPanel.vue'

const route = useRoute()
const router = useRouter()
const product = ref<any>({})

onMounted(async () => { const res = await getReviewProduct(Number(route.params.id)); product.value = res.data })

async function doApprove() { await approveProduct(product.value.id); ElMessage.success('审核通过'); router.push('/reviewer/products') }
async function doReject(reason: string) { await rejectProduct(product.value.id, reason); ElMessage.success('已驳回'); router.push('/reviewer/products') }
</script>
```

- [ ] **Step 4: 创建超管端页面**

`admin/CategoryManage.vue`:
```vue
<template>
  <div>
    <el-button type="primary" @click="openDialog()" style="margin-bottom:16px">新增品类</el-button>
    <el-table :data="tree" border row-key="id">
      <el-table-column prop="name" label="品类名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column prop="status" label="状态" width="80" />
      <el-table-column label="操作" width="200">
        <template #default="{row}">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" @click="openDialog(row, true)">添加子类</el-button>
          <el-button size="small" type="danger" @click="del(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg.visible" :title="dlg.isEdit ? '编辑品类' : '新增品类'" @closed="dlg.form={}">
      <el-form :model="dlg.form">
        <el-form-item label="名称"><el-input v-model="dlg.form.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="dlg.form.description" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="dlg.form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/index'

const tree = ref<any[]>([])
const dlg = reactive({ visible: false, isEdit: false, form: {} as any, parentId: null as number | null })

onMounted(fetchData)
async function fetchData() { const res = await api.get('/categories'); tree.value = flattenTree(res.data) }

function flattenTree(items: any[], result: any[] = []) {
  for (const item of items) { result.push(item); if (item.children?.length) flattenTree(item.children, result) }
  return result
}

function openDialog(row?: any, asChild = false) {
  dlg.visible = true
  if (row && !asChild) { dlg.isEdit = true; dlg.form = { id: row.id, name: row.name, description: row.description, sort_order: row.sort_order } }
  else { dlg.isEdit = false; dlg.form = { name: '', description: '', sort_order: 0 }; dlg.parentId = asChild ? row.id : null }
}

async function save() {
  if (dlg.isEdit) {
    await api.put(`/admin/categories/${dlg.form.id}`, dlg.form)
  } else {
    await api.post('/admin/categories', { ...dlg.form, parent_id: dlg.parentId })
  }
  dlg.visible = false; fetchData(); ElMessage.success('保存成功')
}

async function del(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await api.delete(`/admin/categories/${id}`); fetchData(); ElMessage.success('删除成功')
}
</script>
```

`admin/MerchantManage.vue`:
```vue
<template>
  <PaginationTable :data="list" :total="total" :page="page" :page-size="pageSize" :loading="loading"
                   @page-change="(p:number)=>{page=p;fetch()}" @size-change="(s:number)=>{pageSize=s;fetch()}">
    <el-table-column prop="username" label="用户名" />
    <el-table-column prop="phone" label="手机号" />
    <el-table-column label="状态" width="100">
      <template #default="{row}"><el-tag :type="row.status==='active'?'success':'danger'">{{ row.status==='active'?'启用':'停用' }}</el-tag></template>
    </el-table-column>
    <el-table-column prop="created_at" label="注册时间" />
    <el-table-column label="操作" width="120">
      <template #default="{row}">
        <el-button size="small" :type="row.status==='active'?'danger':''" @click="toggle(row)">{{ row.status==='active'?'停用':'启用' }}</el-button>
      </template>
    </el-table-column>
  </PaginationTable>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/index'
import PaginationTable from '@/components/common/PaginationTable.vue'

const list = ref<any[]>([]); const total = ref(0); const loading = ref(false)
const page = ref(1); const pageSize = ref(20)

onMounted(fetch)
async function fetch() {
  loading.value = true
  try { const res = await api.get('/admin/merchants', { params: { page: page.value, page_size: pageSize.value } }); list.value = res.data.list; total.value = res.data.total }
  finally { loading.value = false }
}

async function toggle(row: any) {
  const newStatus = row.status === 'active' ? 'disabled' : 'active'
  await api.put(`/admin/merchants/${row.id}/status?status=${newStatus}`)
  ElMessage.success('更新成功'); fetch()
}
</script>
```

`admin/ReviewerManage.vue`:
```vue
<template>
  <div>
    <el-button type="primary" @click="dlg.visible=true" style="margin-bottom:16px">新增审核员</el-button>
    <PaginationTable :data="list" :total="total" :page="page" :page-size="pageSize" :loading="loading"
                     @page-change="(p:number)=>{page=p;fetch()}" @size-change="(s:number)=>{pageSize=s;fetch()}">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column label="状态" width="100"><template #default="{row}"><el-tag :type="row.status==='active'?'success':'danger'">{{ row.status }}</el-tag></template></el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
    </PaginationTable>
    <el-dialog v-model="dlg.visible" title="新增审核员" @closed="dlg.form={}">
      <el-form :model="dlg.form">
        <el-form-item label="用户名"><el-input v-model="dlg.form.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="dlg.form.password" type="password" show-password /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="dlg.form.phone" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/index'
import PaginationTable from '@/components/common/PaginationTable.vue'

const list = ref<any[]>([]); const total = ref(0); const loading = ref(false)
const page = ref(1); const pageSize = ref(20)
const dlg = reactive({ visible: false, form: { username: '', password: '', phone: '' } })

onMounted(fetch)
async function fetch() {
  loading.value = true
  try { const res = await api.get('/admin/reviewers', { params: { page: page.value, page_size: pageSize.value } }); list.value = res.data.list; total.value = res.data.total }
  finally { loading.value = false }
}

async function save() {
  await api.post('/admin/reviewers', null, { params: dlg.form })
  dlg.visible = false; fetch(); ElMessage.success('新增成功')
}
</script>
```

`admin/QualificationTypeManage.vue`:
```vue
<template>
  <div>
    <el-button type="primary" @click="openDialog()" style="margin-bottom:16px">新增资质类型</el-button>
    <el-table :data="list" border>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="code" label="编码" />
      <el-table-column prop="scope" label="适用维度" />
      <el-table-column label="必传" width="80"><template #default="{row}"><el-tag :type="row.is_required?'danger':'info'">{{ row.is_required ? '是' : '否' }}</el-tag></template></el-table-column>
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="160">
        <template #default="{row}"><el-button size="small" @click="openDialog(row)">编辑</el-button><el-button size="small" type="danger" @click="del(row.id)">删除</el-button></template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dlg.visible" :title="dlg.isEdit ? '编辑' : '新增'" @closed="dlg.form={}">
      <el-form :model="dlg.form">
        <el-form-item label="名称"><el-input v-model="dlg.form.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="dlg.form.code" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="dlg.form.description" /></el-form-item>
        <el-form-item label="适用维度"><el-select v-model="dlg.form.scope"><el-option label="商家" value="merchant" /><el-option label="商品" value="product" /></el-select></el-form-item>
        <el-form-item label="是否必传"><el-switch v-model="dlg.form.is_required" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="dlg.form.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.visible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/index'

const list = ref<any[]>([])
const dlg = reactive({ visible: false, isEdit: false, form: {} as any })

onMounted(fetchData)
async function fetchData() { const res = await api.get('/admin/qualification-types'); list.value = res.data }

function openDialog(row?: any) {
  dlg.visible = true
  if (row) { dlg.isEdit = true; dlg.form = { ...row } }
  else { dlg.isEdit = false; dlg.form = { name: '', code: '', description: '', scope: 'merchant', is_required: true, sort_order: 0 } }
}

async function save() {
  if (dlg.isEdit) {
    await api.put(`/admin/qualification-types/${dlg.form.id}`, dlg.form)
  } else {
    await api.post('/admin/qualification-types', dlg.form)
  }
  dlg.visible = false; fetchData(); ElMessage.success('保存成功')
}

async function del(id: number) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await api.delete(`/admin/qualification-types/${id}`); fetchData(); ElMessage.success('删除成功')
}
</script>
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/reviewer/ frontend/src/views/admin/
git commit -m "feat: add reviewer and admin pages"
```

---

## Phase 6: 最终集成

### Task 21: 数据库初始化 + 启动验证

- [ ] **Step 1: 安装 Python 依赖**

```bash
cd backend && pip install -r requirements.txt
```

- [ ] **Step 2: 运行数据库迁移**

```bash
cd backend && python -c "from app.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine); print('Tables created')"
```

- [ ] **Step 3: 运行种子数据**

```bash
cd backend && python seed.py
```

- [ ] **Step 4: 启动后端服务**

```bash
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**预期:** 服务启动在 http://127.0.0.1:8000，访问 http://127.0.0.1:8000/docs 可看到 Swagger 文档

- [ ] **Step 5: 安装前端依赖并启动**

```bash
cd frontend && npm install && npm run dev
```

**预期:** 前端启动在 http://localhost:5173

- [ ] **Step 6: 端到端验证**

1. 浏览器访问 http://localhost:5173 → 显示登录页
2. 用 merchant/merchant123 登录 → 进入商家工作台
3. 发布一个商品 → 填写所有步骤 → 提交审核
4. 退出 → 用 reviewer/review123 登录 → 审核列表 → 审核通过
5. 退出 → 用 admin/admin123 登录 → 管理品类/用户

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: complete project integration"
```

---

## 完整性检查清单

- [ ] 后端 40+ API 全部可用，Swagger 文档可测试
- [ ] 前端 3 角色页面完整，路由守卫生效
- [ ] JWT 登录认证 + 角色权限控制
- [ ] 商品分步表单 + 草稿自动保存
- [ ] 图片/文件上传 + 预览
- [ ] 审核列表多维筛选 + 批量操作
- [ ] 版本历史时间线
- [ ] 资质到期检查定时任务
- [ ] 商家 dashboard 统计
- [ ] 审核员 dashboard 统计
- [ ] 超管品类/用户/资质类型 CRUD
