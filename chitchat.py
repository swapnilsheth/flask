#https://blog.devgenius.io/a-simple-way-to-build-flask-file-upload-1ccb9462bc2c
import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from chat_processing_test_sb import chat_processing

app=Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt'])

def process_chat(filename, file_location):
    x = chat_processing.read_file(filename, file_location)
    y = chat_processing.text_clean(x)
    z=chat_processing.convert_to_df(y)
    a = chat_processing.df_enhance(z)
    b = chat_processing.visualizations(a)
    return

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/results')
def results():
    return render_template('results.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_chat(filename, UPLOAD_FOLDER)
            flash('File successfully uploaded')
            return redirect('/results')
        else:
            flash('Only txt file is allowed')
            return redirect(request.url)



if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 5000, debug = False)
