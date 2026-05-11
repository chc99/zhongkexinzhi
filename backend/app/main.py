from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Scheduler will be started here in Task 4
    yield
    # Scheduler will be shutdown here in Task 4


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers will be registered in Task 4
# Static files mount for uploads
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Register routers - use try/except for modules not yet created
# These will be replaced with direct imports as modules are created
router_modules = [
    ("app.api.auth", "auth_router"),
    ("app.api.upload", "upload_router"),
    ("app.api.categories", "categories_router"),
    ("app.api.merchant.products", "merchant_product_router"),
    ("app.api.merchant.qualifications", "merchant_qual_router"),
    ("app.api.reviewer.products", "reviewer_router"),
    ("app.api.admin.categories", "admin_category_router"),
    ("app.api.admin.merchants", "admin_merchant_router"),
    ("app.api.admin.qualification_types", "admin_qual_type_router"),
]

for module_name, var_name in router_modules:
    try:
        module = __import__(module_name, fromlist=[var_name])
        router = getattr(module, var_name)
        app.include_router(router, prefix="/api")
    except (ImportError, AttributeError):
        pass  # Module not created yet


@app.get("/")
def root():
    return {"code": 200, "message": "保健品商家后台管理系统 API", "data": None}
