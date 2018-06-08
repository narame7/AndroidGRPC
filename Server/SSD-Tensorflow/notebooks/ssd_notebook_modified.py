# coding: utf-8

import os
import math
import random

import numpy as np
import tensorflow as tf
import cv2

slim = tf.contrib.slim

#get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import sys
sys.path.append('../')

from nets import ssd_vgg_300, ssd_common, np_methods
from preprocessing import ssd_vgg_preprocessing
import visualization
#from notebooks import visualization

import pickle 
import cv2

import time
from concurrent import futures

import grpc
import exchange_frame_pb2
import exchange_frame_pb2_grpc

# TensorFlow session: grow memory when needed. TF, DO NOT USE ALL MY GPU MEMORY!!!
gpu_options = tf.GPUOptions(allow_growth=True)
config = tf.ConfigProto(log_device_placement=False, gpu_options=gpu_options)
isess = tf.InteractiveSession(config=config)


# ## SSD 300 Model
# 
# The SSD 300 network takes 300x300 image inputs. In order to feed any image, the latter is resize to this input shape (i.e.`Resize.WARP_RESIZE`). Note that even though it may change the ratio width / height, the SSD model performs well on resized images (and it is the default behaviour in the original Caffe implementation).
# 
# SSD anchors correspond to the default bounding boxes encoded in the network. The SSD net output provides offset on the coordinates and dimensions of these anchors.

# Input placeholder.
net_shape = (300, 300)
data_format = 'NHWC'
img_input = tf.placeholder(tf.uint8, shape=(None, None, 3))
# Evaluation pre-processing: resize to SSD net shape.
image_pre, labels_pre, bboxes_pre, bbox_img = ssd_vgg_preprocessing.preprocess_for_eval(
    img_input, None, None, net_shape, data_format, resize=ssd_vgg_preprocessing.Resize.WARP_RESIZE)
image_4d = tf.expand_dims(image_pre, 0)


# Define the SSD model.
reuse = True if 'ssd_net' in locals() else None
ssd_net = ssd_vgg_300.SSDNet()
with slim.arg_scope(ssd_net.arg_scope(data_format=data_format)):
    predictions, localisations, _, _ = ssd_net.net(image_4d, is_training=False, reuse=reuse)

# Restore SSD model.
ckpt_filename = '../checkpoints/ssd_300_vgg.ckpt'
# ckpt_filename = '../checkpoints/VGG_VOC0712_SSD_300x300_ft_iter_120000.ckpt'
isess.run(tf.global_variables_initializer())
saver = tf.train.Saver()
saver.restore(isess, ckpt_filename)

# SSD default anchor boxes.
ssd_anchors = ssd_net.anchors(net_shape)


# ## Post-processing pipeline
# 
# The SSD outputs need to be post-processed to provide proper detections. Namely, we follow these common steps:
# 
# * Select boxes above a classification threshold;
# * Clip boxes to the image shape;
# * Apply the Non-Maximum-Selection algorithm: fuse together boxes whose Jaccard score > threshold;
# * If necessary, resize bounding boxes to original image shape.

# Main image processing routine.
def process_image(img, select_threshold=0.65, nms_threshold=.45, net_shape=(300, 300)):
    # Run SSD network.
    rimg, rpredictions, rlocalisations, rbbox_img = isess.run([image_4d, predictions, localisations, bbox_img],
                                                              feed_dict={img_input: img})
    
    # Get classes and bboxes from the net outputs.
    rclasses, rscores, rbboxes = np_methods.ssd_bboxes_select(
            rpredictions, rlocalisations, ssd_anchors,
            select_threshold=select_threshold, img_shape=net_shape, num_classes=21, decode=True)
    
    rbboxes = np_methods.bboxes_clip(rbbox_img, rbboxes)
    rclasses, rscores, rbboxes = np_methods.bboxes_sort(rclasses, rscores, rbboxes, top_k=400)
    rclasses, rscores, rbboxes = np_methods.bboxes_nms(rclasses, rscores, rbboxes, nms_threshold=nms_threshold)
    # Resize bboxes to original image shape. Note: useless for Resize.WARP!
    rbboxes = np_methods.bboxes_resize(rbbox_img, rbboxes)
    return rclasses, rscores, rbboxes


# Added ----------------------------------------------------------------------


VOC_LABELS = {
    'none': (0, 'Background'),
    'aeroplane': (1, 'Vehicle'),
    'bicycle': (2, 'Vehicle'),
    'bird': (3, 'Animal'),
    'boat': (4, 'Vehicle'),
    'bottle': (5, 'Indoor'),
    'bus': (6, 'Vehicle'),
    'car': (7, 'Vehicle'),
    'cat': (8, 'Animal'),
    'chair': (9, 'Indoor'),
    'cow': (10, 'Animal'),
    'diningtable': (11, 'Indoor'),
    'dog': (12, 'Animal'),
    'horse': (13, 'Animal'),
    'motorbike': (14, 'Vehicle'),
    'person': (15, 'Person'),
    'pottedplant': (16, 'Indoor'),
    'sheep': (17, 'Animal'),
    'sofa': (18, 'Indoor'),
    'train': (19, 'Vehicle'),
    'tvmonitor': (20, 'Indoor'),
}

class2label = {}

for key in VOC_LABELS.keys():
    class2label[VOC_LABELS[key][0]] = key

#### GRPC Service (by Sang-ki Ko on 2018/3/9)

key = 0
#arr = ["5","0.99","0.2","0.2","0.6","0.6"]

class VideoStreamer(exchange_frame_pb2_grpc.VideoStreamerServicer):
    def VideoProcess(self, request, context):

        img = pickle.loads(request.frame)

        img = cv2.flip(img, 1)
        #img = frame
        rclasses, rscores, rbboxes =  process_image(img, 0.3)
	    
        visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_tableau, class2label, thickness=2)

        frameBytes = pickle.dumps(img)

        return exchange_frame_pb2.OutputVideo(frame=frameBytes)

    def VideoProcessFromC(self, request, context):
        nparr = np.fromstring(request.frame, dtype=np.uint8)
        nparr = np.reshape(nparr, (480, 640, 3), order='C')

        img = cv2.flip(nparr, 1)
        #img = frame
        rclasses, rscores, rbboxes =  process_image(img, 0.3)
	    
        visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_tableau, class2label, thickness=2)

        return exchange_frame_pb2.OutputVideo(frame=img.tobytes())

    def VideoProcessFromAndroid(self, request_iterator, context):
        start = time.time()
        for i in request_iterator:
            result = []
            global key
            videoFrame = np.array(list(i.frame))
            videoFrame = videoFrame.reshape(300, 300, 3)
            videoFrame = np.array(videoFrame, dtype=np.uint8)
            rows, cols = videoFrame.shape[:2]
            M = cv2.getRotationMatrix2D((cols/2, rows/2), 270, 1)
            image = cv2.warpAffine(videoFrame, M, (cols, rows))
            key = key + 1

            rclasses, rscores, rbboxes =  process_image(image, 0.3)
            for i in range(rbboxes.shape[0]):
                bbox = rbboxes[i]
                classes = '%s' % (rclasses[i])
                scores = '%.3f' % (rscores[i])
                bbox1 = '%.3f' % (bbox[0])
                bbox2 = '%.3f' % (bbox[1])
                bbox3 = '%.3f' % (bbox[2])
                bbox4 = '%.3f' % (bbox[3])
                result.extend([classes, scores, bbox1, bbox2, bbox3, bbox4])

            #print(result)
            #print(rclasses)
            #print(type(rclasses[0]))
            #print(rscores)
            #print(type(rscores[0]))
            #print(rbboxes)
            #print(type(rbboxes))
            #print(type(rbboxes[0]))
            print(key)

        for i in result:
            yield exchange_frame_pb2.BoundingBox(info=i)
        end = time.time()
        print(end-start)



USE_WEBCAM = True

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

if USE_WEBCAM:

	# cap = cv2.VideoCapture(0)
	# print(cap.get(3), cap.get(4))
	# cap.set(3, 1920)
	# cap.set(4, 1080)
	# cap.set(3, 640)
	# cap.set(4, 480)
	# print(cap.get(3), cap.get(4))


    colors = dict()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    exchange_frame_pb2_grpc.add_VideoStreamerServicer_to_server(VideoStreamer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
'''
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

	    # Our operations on the frame come here
	    #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        img = cv2.flip(frame, 1)
        #img = frame
        rclasses, rscores, rbboxes =  process_image(img, 0.3)
	    
        visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_tableau, class2label, thickness=2)
	    
        # Display the resulting frame
        cv2.imshow('frame', img)
	    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


else:
    #img = cv2.imread('messi5.jpg',0)
    path = '../demo/'
    mage_names = sorted(os.listdir(path))

    img = cv2.imread(path + image_names[-5], 1)
    rclasses, rscores, rbboxes =  process_image(img)

    # visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_plasma)
    #visualization.plt_bboxes(img, rclasses, rscores, rbboxes)
    visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_tableau, class2label, thickness=2)

    cv2.imshow('image', img)
    cv2.waitKey(0) & 0xFF == ord('q')
    cv2.destroyAllWindows()
'''
# ----------------------------------------------------------------------------

'''
# Test on some demo image and visualize output.
path = '../demo/'
image_names = sorted(os.listdir(path))

img = mpimg.imread(path + image_names[-5])
rclasses, rscores, rbboxes =  process_image(img)

# visualization.bboxes_draw_on_img(img, rclasses, rscores, rbboxes, visualization.colors_plasma)
visualization.plt_bboxes(img, rclasses, rscores, rbboxes)
'''

