from .ObjectDetector import detectImages, detectVideos
import io
from PIL import Image
import os
from werkzeug.utils import secure_filename

from flask import render_template, request, Response, send_file, redirect
from myapp import myapp

import time
import uwsgi
import git
import subprocess

#app = Flask(__name__)
UPLOAD_FOLDER = 'myapp/static:css/uploads/'

# paste camera stream url in quotations ("url") or use 0 to use webcam 
cam_url = os.getenv('CAMERA_STREAM_URL', '0')

@myapp.route("/")
def index():
    return render_template('index.html')

@myapp.route('/live_stream', methods=["GET"])
def live_stream():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(detectVideos(cam_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@myapp.route("/", methods=['POST'])
def upload():
    if request.form['dtype']=='image':
        imName=Image.open(request.files['file'].stream)
        img = detectImages(imName)
        return send_file(io.BytesIO(img),attachment_filename='image.jpg',mimetype='image/jpg')

    elif request.form['dtype']=='video':
        myapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        file=request.files['file']
        filename = secure_filename(file.filename)
        new_filename = os.path.join(myapp.config['UPLOAD_FOLDER'], filename)
        file.save(new_filename)
        return Response(detectVideos(str(new_filename)),
                mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return redirect(f"/live_stream")
        #Response(detectVideos(cam_url),
        #        mimetype='multipart/x-mixed-replace; boundary=frame')

@myapp.route("/update", methods = ["POST"])
def update():
    if request.method == 'POST':
        g = git.cmd.Git('/home/duyguay/object detection api')
        g.pull()
        time.sleep(5)
        #uwsgi.reload()
        print('hello')
        subprocess.call(['sudo docker-compose.exe','restart'])
        return ''

if __name__ == "__main__":
    myapp.run(debug=True)
