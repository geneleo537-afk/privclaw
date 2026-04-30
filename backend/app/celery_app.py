"""
Celery 应用实例。

Worker 启动命令：celery -A app.celery_app worker --loglevel=info
任务在 app/tasks/ 目录下定义，通过 include 参数自动发现。
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "privclaw",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.order_timeout",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
    # 任务结果保留时间：24 小时
    result_expires=86400,
    # 防止任务重复执行：acks_late=True 确保任务执行成功后才确认
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
