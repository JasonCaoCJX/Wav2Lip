from celery import Celery
import time

celery = Celery('tasks', broker='redis://localhost:6379/0', result_backend='redis://localhost:6379/0')
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_concurrency = 2

@celery.task
def generate_video():
    total_time = 60
    for i in range(total_time):
        time.sleep(1)
        progress = (i + 1) / total_time * 100
        print(f"Task progress: {progress}%")
    return "test"
