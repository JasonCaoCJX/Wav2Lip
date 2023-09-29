from celery import Celery
from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from tasks import generate_video
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

celery = Celery('tasks', broker='redis://localhost:6379/0', result_backend='redis://localhost:6379/0')
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_concurrency = 2

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://magic.xinvtech.cn')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,ngrok-skip-browser-warning')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/generate', methods=['POST'])
def generate():
    # video_path = 'input/2.mp4'
    # audio_path = 'input/1.wav'
    data = request.get_json()
    face = data.get('face')
    voice = data.get('voice')
    model = data.get('model')

    video_path = 'upload/face/' + face
    audio_path = 'upload/voice/' + voice
    print(video_path, audio_path)
    
    # result = generate_video.delay(video_path, audio_path, 'checkpoints/wav2lip.pth')

    task = generate_video.delay(video_path, audio_path, model)
    status, active, total = get_task_count()
    return {"id": task.id, "face": face, "voice": voice, "status": {"status": status, "work": active, "total": total}}

@app.route('/progress/<task_id>', methods=['GET'])
def progress(task_id):
    task = celery.AsyncResult(task_id)
    # i = celery.control.inspect()
    # active = list(i.active().values())[0]
    # reserved = list(i.reserved().values())[0]
    # print(active, reserved)
    print(task.status)
    if task.ready():
        # 获取任务返回值
        task_result = task.get()
        response = {'status': 'SUCCESS', 'video': task_result}
        # response = {'status': 'SUCCESS'}
    else:
        response = {'status': 'PENDING'}

    return response
    

@app.route('/uploadface', methods=['POST'])
def uploadface():
    files = request.files.getlist('file')
    timestamp = int(round(time.time() * 1000))

    for file in files:
        extension = file.filename.split('.')[-1]
        filename = str(timestamp) + "." + extension
        file.save("upload/face/" + filename)
        
    return filename
        

@app.route('/uploadvoice', methods=['POST'])
def uploadvoice():
    files = request.files.getlist('file')
    timestamp = int(round(time.time() * 1000))

    for file in files:
        extension = file.filename.split('.')[-1]
        filename = str(timestamp) + "." + extension
        file.save("upload/voice/" + filename)
        
    return filename

@app.route('/getface/<filename>', methods=['GET'])
def getface(filename):
    print(filename)
    return send_from_directory("upload/face/", filename)

@app.route('/getvoice/<filename>', methods=['GET'])
def getvoice(filename):
    print(filename)
    return send_from_directory("upload/voice/", filename)

@app.route('/getresult/<filename>', methods=['GET'])
def getresult(filename):
    print(filename)
    return send_from_directory("results/", filename)

@app.route('/status', methods=['GET'])
def getStatus():
    status, active, total = get_task_count()
    return {"status": status, "work": active, "total": total}
    

def get_task_count():
    try:
        i = celery.control.inspect()
        active = list(i.active().values())[0]
        reserved = list(i.reserved().values())[0]
        return "RUNNING", len(active), len(reserved) + len(active)
        
    except:
        return "ERROR", 0, 0
    



if __name__ == '__main__':
    app.run(port=5001)


# celery -A tasks worker -l info -P eventlet