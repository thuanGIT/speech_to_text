import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from speech import handle_large_audio, write_to_file

main_page = '''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    h1 {text-align: center;}
    p {text-align: center;}
    div {text-align: center;}
    form {text-align: center;}
    </style>
    </head>
    <h1>Upload your lecture</h1>
    <p>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </p>
    </body>
    </html>
    '''
UPLOAD_FOLDER = '/assets/audio'
DOWNLOAD_FOLDER = '/assets/out'
ALLOWED_EXTENSIONS = {'m4a', 'wav','mp4','mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', filename=filename))
    return main_page 

@app.route('/uploads/<filename>')
def download_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    result = handle_large_audio(path)
    write_to_file(result)
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)


@app.route('/letter')
def send_letter():
    page = ''' 
    <!DOCTYPE html>
    <html>
    '''
    
    return page


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)