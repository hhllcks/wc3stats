from flask import Flask, render_template, request
from flask.ext.uploads import UploadSet, configure_uploads, ALL

app = Flask(__name__)

files = UploadSet('files', ALL)

app.config['UPLOADED_FILES_DEST'] = 'uploads'
configure_uploads(app, files)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'media' in request.files:
        filename = files.save(request.files['media'])

    return render_template('upload.html')

if __name__ == '__main__':
	app.run(debug=True)