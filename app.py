from flask import Flask, redirect, render_template, request, session, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_dropzone import Dropzone
from keras.models import load_model
import tensorflow as tf
import cv2
import numpy as np
import os
from keras import backend as K
app = Flask(__name__)
dropzone = Dropzone(app)


app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

# Dropzone settings
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

@app.route('/', methods=['GET', 'POST'])
def index():
    
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
    # list to hold our uploaded image urls
    file_urls = session['file_urls']

    # handle image upload from Dropszone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            
            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename    
            )

            # append image urls
            file_urls.append(photos.url(filename))
            
        session['file_urls'] = file_urls
        print("file_uplod")
        return "uploading..."
    # return dropzone template on GET request    
    return render_template('index.html')


@app.route('/results')
def results():
    
    # redirect to home if no images to display
    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('index'))
        
    # set the file_urls and remove the session variable
    file_urls = session['file_urls']
    session.pop('file_urls', None)
    for i in range(len(file_urls)):
        img = "uploads/"+file_urls[i].split("photos/")[-1]
        img1= img
        img = cv2.imread(img)
        img = cv2.resize(img,(256,256))
        img = np.reshape(img,[1,256,256,3])
        K.clear_session()
        model = load_model('model_weights.h5')
        graph = tf.get_default_graph()
        classes = model.predict_classes(img)
        if classes[0]==1:
            ravi="Given leaf is diseased"
        else:
            ravi="Given leaf is undiseased"
        print("--------------------")
        file_urls[i]=(file_urls[i],ravi)
    return render_template('results.html', file_urls=file_urls)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
