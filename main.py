import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from speech import handle_large_audio, write_to_file

UPLOAD_FOLDER = 'assets/audio'
DOWNLOAD_FOLDER = 'assets/download'
ALLOWED_EXTENSIONS = {'m4a', 'wav','mp4','mp3'}
result_file = 'result.txt'

app = Flask(__name__, template_folder='templates', static_folder='static')
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
            #print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Check if the file's name is safe
            filename = secure_filename(file.filename)

            # Save file to folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as fp:
            #     fp.write(file)
            print("saved file successfully") # Debugging

            # Process the audio
            process(filename)

            return redirect(url_for('download_file', filename=filename))
    return render_template('mainpage.html')

@app.route('/download/<filename>', methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)
    

@app.route('/result/<filename>')
def get_result(filename):
    # Debugging
    print(f"Downloading {filename}.txt")
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename=result_file, as_attachment=True)

def process(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    result = handle_large_audio(path)

    # Modify filename
    write_to_file(result, filename=result_file)



if __name__ == "__main__":
    import sys
    sys.path.append('config/ffmpeg')
    port = int(os.environ.get("PORT", 5000)) # Default port is 5000
    app.run(host='0.0.0.0', port=port)

    