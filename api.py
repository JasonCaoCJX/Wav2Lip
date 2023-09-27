from celery import Celery
from flask import Flask, jsonify, request
from flask_cors import CORS
from tasks import generate_video
import time

app = Flask(__name__)
CORS(app)

celery = Celery('tasks', broker='redis://localhost:6379/0', result_backend='redis://localhost:6379/0')
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_concurrency = 2

# @app.route('/generate', methods=['POST'])
# def generate():
#     # video_file = request.files['video']
#     # audio_file = request.files['audio']
#     video_path = 'input/1.mp4'
#     audio_path = 'input/1.wav'
#     # video_file.save(video_path)
#     # audio_file.save(audio_path)
    
#     result = generate_video.delay(video_path, audio_path, 'checkpoints/wav2lip.pth')
    
#     return result.id

@app.route('/generate', methods=['GET'])
def generate():
    video_path = 'input/2.mp4'
    audio_path = 'input/1.wav'
    
    # result = generate_video.delay(video_path, audio_path, 'checkpoints/wav2lip.pth')
    task = generate_video.delay()
    active, total = get_task_count()
    return {"id": task.id, "work": active, "total": total}

@app.route('/progress/<task_id>', methods=['GET'])
def progress(task_id):
    task = celery.AsyncResult(task_id)
    i = celery.control.inspect()
    active = list(i.active().values())[0]
    reserved = list(i.reserved().values())[0]
    print(active, reserved)
    if task.ready():
        status = task.state
    else:
        status = task.state
    return jsonify({'status': status})


    # if task.state == 'PENDING':
    #     response = {'status': 'waiting', 'progress': 0}
    # elif task.state == 'STARTED':
    #     response = {'status': 'working', 'progress': task.info.get('progress', 0)}
    # elif task.state == 'SUCCESS':
    #     response = {'status': 'finish', 'progress': 100}
    # else:
    #     response = {'status': 'error', 'message': task.info.get('error', 'Unknown error')}

    # return jsonify(response)

@app.route('/uploadface', methods=['POST'])
def uploadface():
    files = request.files.getlist('file')
    timestamp = int(round(time.time() * 1000))
    print(timestamp)
    print(files)
    for file in files:
        extension = file.filename.split('.')[-1]
        filename = str(timestamp) + "." + extension
        file.save("upload/face/" + filename)
    
    return filename

@app.route('/uploadvoice', methods=['POST'])
def uploadvoice():
    files = request.files.getlist('file')
    timestamp = int(round(time.time() * 1000))
    print(timestamp)
    print(files)
    for file in files:
        extension = file.filename.split('.')[-1]
        filename = str(timestamp) + "." + extension
        file.save("upload/voice/" + filename)
    
    return filename


def get_task_count():
    i = celery.control.inspect()
    active = list(i.active().values())[0]
    reserved = list(i.reserved().values())[0]
    return len(active), len(reserved) + len(active)



if __name__ == '__main__':
    app.run(port=5001)


# celery -A tasks worker -l info -P eventlet