"""Initialize seed data: admin/reviewer/merchant accounts, default categories, qualification types"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models import *
from app.models.user import User, UserRole, UserStatus
from app.models.category import Category, CategoryStatus
from app.models.qualification_type import QualificationType, QualScope
from app.services.auth_service import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create default users
default_users = [
    ("admin", "admin123", UserRole.admin, ""),
    ("reviewer", "review123", UserRole.reviewer, ""),
    ("merchant", "merchant123", UserRole.merchant, ""),
]
for username, password, role, phone in default_users:
    if not db.query(User).filter(User.username == username).first():
        db.add(User(username=username, password_hash=hash_password(password), role=role, phone=phone))
        db.flush()
        print(f"Created user: {username} / {password}")

# Create default categories
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
        db.flush()
        print(f"Created category: {name}")

# Create default qualification types
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
        qt = QualificationType(name=name, code=code, description=desc, is_required=required, scope=QualScope(scope), sort_order=i)
        db.add(qt)
        db.flush()
        print(f"Created qualification type: {name}")

db.commit()
db.close()
print("\nSeed data complete!")
print("Default accounts: admin/admin123 | reviewer/review123 | merchant/merchant123")
