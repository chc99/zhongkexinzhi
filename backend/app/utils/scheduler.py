from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_settings

scheduler = BackgroundScheduler()
settings = get_settings()


def check_qualification_expiry():
    from app.database import SessionLocal
    from app.models.merchant_qualification import MerchantQualification
    from app.models.product_qualification import ProductQualification, QualStatus

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
            ).update({model.status: QualStatus.expiring}, synchronize_session=False)

            # 已过期: expire_date < 今天
            db.query(model).filter(
                model.expire_date < today,
                model.status.in_([QualStatus.valid, QualStatus.expiring])
            ).update({model.status: QualStatus.expired}, synchronize_session=False)

        db.commit()
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_qualification_expiry, "cron", hour=2, minute=0, id="check_expiry", replace_existing=True)
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown()
