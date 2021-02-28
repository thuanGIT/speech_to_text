import os
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
from celery import Celery
import speech
from dotenv import load_dotenv

# Setting for environment from .env
# Not applicable with heroku
load_dotenv()

UPLOAD_FOLDER = 'assets/audio'
DOWNLOAD_FOLDER = 'assets/download'
ALLOWED_EXTENSIONS = {'m4a', 'wav','mp4','mp3'}


# Flask app config
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
app.config['CELERY_RESULT_BACKEND'] = os.environ['CELERY_RESULT_BACKEND']

# Celery config
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            #print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Check if the file's name is safe
            filename = secure_filename(file.filename)

            # Save file to folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully") # Debugging

            return redirect(url_for('show_status', filename=filename))
    return render_template('mainpage.html')

@app.route('/start/<filename>', methods=['POST'])
def start_task(filename):
    # Process the audio
    task = process.apply_async(args=[filename])
    # Code 202 means task is in progress
    return jsonify({}), 202, {'Location': url_for('get_status',task_id=task.id)}


@app.route('/download/<filename>', methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)
    
@app.route('/result/<filename>')
def get_result(filename):
    # Debugging
    print(f"Downloading {filename}.txt")
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename=speech.result_file, as_attachment=True)

@app.route('/status/<task_id>')
def get_status(task_id):
    task = process.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE': # could be STARTED, RETRY, SUCCESS
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

    # return redirect(url_for('download_file'), filename=filename)

@app.route('/status/<filename>')
def show_status(filename):
    return render_template('status.html', value=filename)

@celery.task(bind=True) # This instructs Celery to send a self argument to my function for status update
def process(self, filename):
    result = speech.handle_large_audio(self, filename=os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return result
    

def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS
   

if __name__ == "__main__":
    print("Starting app")
    port = int(os.environ.get("PORT", 5000)) # Default port is 5000
    app.run(host='0.0.0.0', port=port)

