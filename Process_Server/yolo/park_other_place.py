from yolo.yolo_methods import *
import os
import cv2
import time
from firebase_update import *
import darknet as dn
import pickle as pkl


CAR_OTHER_PLACE_TIME = time.time()
def yolo_model_load(read_cfg='yolov3-tiny.cfg',
                    read_weight='yolov3-tiny.weights', read_data='coco.data'):
    net = dn.load_net(read_cfg.encode('utf-8'), read_weight.encode('utf-8'), 0)
    meta = dn.load_meta(read_data.encode('utf-8'))
    return net, meta

def detection_park_other_place(yolo_net, yolo_meta, input_data, sec_center, sec_img):
    center = sec_center.get()
    img = sec_img.get()
    illegal_car_count = 0
    with open('pts.pkl', 'rb') as fr:
        pts_list = pkl.load(fr)
    for i in range(len(input_data)):
        center[i], img[i], cnt = check_section(input_data[i],
                                                       center[i], 
                                                       img[i], 
                                                       yolo_meta, 
                                                       yolo_net)
        print('section {} illegal count : {}'.format(i+1,cnt))
        illegal_car_count += cnt
    sec_center.put(center)
    sec_img.put(img)
    print('illegal_car_count :', illegal_car_count)
    fire_base_illegal(illegal_car_count)
