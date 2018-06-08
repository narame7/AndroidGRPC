import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# For image captioing

import numpy as np
import skimage.io as io
import time
import progressbar
import h5py
import json
from keras.preprocessing import image
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
from keras.applications.imagenet_utils import _obtain_input_shape


def getImageCnnModel():
    model = ResNet50(include_top=True, weights='imagenet')
    cnn_output_len = 2048
    model.layers.pop()
    model.outputs = [model.layers[-1].output]
    model.output_layers = [model.layers[-1]]
    model.layers[-1].outbound_nodes = []
    return [model, cnn_output_len]


import sys

sys.path.insert(0, './resnet/')
from resnet50 import identity_block, ResNet50

[model, cnn_output_len] = getImageCnnModel()

filename_info = './preData/kout.json'
f = open(filename_info, 'r')
fline = f.read()
config = json.loads(fline)
print(config.keys())
images_json = config['images']
wtoi = config['word_to_ix']
itow = config['ix_to_word']
BOS_Token = wtoi['<start>']
EOS_Token = wtoi['<eos>']

h_train = './preData/ktrainset.h5'
data_h = h5py.File(h_train)
icapsShape = data_h['caps'].shape
icaptlen = icapsShape[1]
tok_num = len(wtoi) + 1
text_tstep = icaptlen - 1
image_tstep = text_tstep
print(text_tstep)

from ImageCaptionModel_DeLSTM import GetImageCaptionModel_ModAPI

ImageCaptionModel = GetImageCaptionModel_ModAPI(cnn_output_len, text_tstep, text_tstep, tok_num,
                                                './input/weights_model_new.best_kor.hdf5')
ImageCaptionModel.summary()

image_id = 410328
img_dir = './demo_images'
img_path = img_dir + '/COCO_val2014_%012d.jpg' % (image_id)


def imageToCaption(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_data = img

    print("Image Feature Extraction")
    img = np.array(img_data)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    # print('Input image shape:', x.shape)
    preds = model.predict(x)
    out = np.reshape(preds, cnn_output_len)

    test_y = np.zeros(text_tstep)
    test_y[0] = BOS_Token
    test_image = np.reshape(out, cnn_output_len)
    test_text = np.reshape(test_y, text_tstep)

    print("Image Caption Inference")

    predictd_caption = ''

    image_t = np.reshape(test_image, (1, cnn_output_len))
    text_t = np.reshape(test_text, (1, image_tstep))

    for idx1 in range(image_tstep - 1):
        out = ImageCaptionModel.predict([image_t, text_t], verbose=0)
        tmp_set = out[0][idx1]
        out_val = np.argmax(tmp_set)
        if out_val == EOS_Token:
            break;
        text_t[0][idx1 + 1] = out_val
        if out_val == 0:
            continue

        # predictd_caption = predictd_caption + " " +str(itow[str(out_val)])
        predictd_caption = predictd_caption + " " + itow[str(out_val)]
        # print(itow[str(out_val)])
        if out_val == EOS_Token:
            break;

    ImageCaptionModel.reset_states()
    print(predictd_caption)
    return predictd_caption


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('template.html')

'''
<!doctype html>
<title>Upload new File</title>
<h1>Upload new File</h1>
<form action="" method=post enctype=multipart/form-data>
<p><input type=file name=file>
<input type=submit value=Upload>
</form>
'''

@app.route('/show/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
       	    filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))

    caption = imageToCaption('static/' + filename)
    # filename = 'http://10.0.0.110:5000/uploads/' + filename
    return render_template('template.html', filename=filename, caption=caption)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=50051)

