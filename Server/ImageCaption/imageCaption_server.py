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
from keras import backend as K

from concurrent import futures

import time

import grpc
import imageCaption_Proto_pb2
import imageCaption_Proto_pb2_grpc

from gtts import gTTS

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
chunk = 1024

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

graph = K.get_session().graph

#image_id = 410328
#img_dir = './demo_images'
#img_path = img_dir + '/COCO_val2014_%012d.jpg' % (image_id)


def imageToCaption(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_data = img

    img = np.array(img_data)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    # print('Input image shape:', x.shape)
    global graph
    with graph.as_default():
        preds = model.predict(x)
        out = np.reshape(preds, cnn_output_len)

        test_y = np.zeros(text_tstep)
        test_y[0] = BOS_Token
        test_image = np.reshape(out, cnn_output_len)
        test_text = np.reshape(test_y, text_tstep)

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
        return predictd_caption

def gttsConverter(msg):
    tts = gTTS(text=msg, lang='ko')
    tts.save("image_test/testSound.mp3")
    data = open("image_test/testSound.mp3", "rb").readlines()
    return data

class GrpcService(imageCaption_Proto_pb2_grpc.imageCaptioningServicer):
    def DataStreaming(self, request_iterator, context):
        print("connect to client...")
        with open('image_test/test.jpg', 'wb') as f:
            try:
                for request in request_iterator:
                    f.write(request.imageData)

            except Exception as e:
                print(e)

        f.close()
        path = "image_test/test.jpg"
        text = imageToCaption(path)
        data = gttsConverter(text)
        print(text)
        for i in data:
            yield imageCaption_Proto_pb2.Response(audioData = i)
#        for i in range(0,1):
        yield imageCaption_Proto_pb2.Response(resultText = text)


def start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    imageCaption_Proto_pb2_grpc.add_ImageCaptioningServicer_to_server(GrpcService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server start...")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    start()
