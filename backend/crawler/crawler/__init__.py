from .celery import app as celery_app

# Import Celery when django starts
__all__ = ("celery_app",)
