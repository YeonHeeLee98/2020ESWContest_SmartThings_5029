from yolo import *
import os
import cv2
import time
from firebase_test import *
import darknet as dn
import pickle as pkl

flag_list = [2, 3, 2, 4]

sec_center = [[], [], [], []]
sec_img = [[], [], [], []]
CAR_OTHER_PLACE_TIME = time.time()
def yolo_model_load(read_cfg='yolov3-tiny.cfg',
                    read_weight='yolov3-tiny.weights', read_data='coco.data'):
    net = dn.load_net(read_cfg.encode('utf-8'), read_weight.encode('utf-8'), 0)
    meta = dn.load_meta(read_data.encode('utf-8'))
    return net, meta

def detection_park_other_place(yolo_net, yolo_meta, dir_list):
    illegal_car_count = 0
    park_other_place = True
    with open('pts.pkl', 'rb') as fr:
        pts_list = pkl.load(fr)
    while True:
        if park_other_place:
            file_list = []
            for folder_name in dir_list:
                file_name = sorted([folder_name + f for f in os.listdir(folder_name) if f[-3:] == 'jpg'])
                file_list.append(file_name[-1])
            print('file_list length :', len(file_list))
            for i in range(len(file_list)):
                print(file_list[i])
                sec_center[i], sec_img[i], cnt = check_section(file_list[i], pts_list[i], flag_list[i],
                                                               sec_center[i], sec_img[i], yolo_meta, yolo_net)
                print(cnt)
                illegal_car_count += cnt
            print('illegal_car_count :', cnt)
            fire_base_illegal(illegal_car_count)
            park_other_place = False
        elif time.time() - CAR_OTHER_PLACE_TIME > 600:
            park_other_place = True
