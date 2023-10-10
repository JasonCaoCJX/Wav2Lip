from celery import Celery, current_task
import time
import subprocess


celery = Celery('tasks', broker='redis://localhost:6379/0', result_backend='redis://localhost:6379/0')
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_concurrency = 2

@celery.task
def generate_video(video_path, audio_path, model):
    task_id = current_task.request.id

    result_path = f'results/{task_id}.mp4'
    print(task_id, model)
    
    command = f'python inference.py --checkpoint_path checkpoints/{model} --face {video_path} --audio {audio_path} --outfile {result_path}'
    subprocess.run(command, shell=True)

    return f"{task_id}.mp4"
