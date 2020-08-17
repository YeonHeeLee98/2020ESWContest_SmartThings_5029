import vid_server
import time
import multiprocessing
from queue import Queue
import cv2
import os
import numpy as np
from pprint import pprint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_test import *
import pickle as pkl
from yolo.yolo_methods import *
import tensorflow as tf
from CarUtility.car_obs import *
from CarPlate.car_number_model import * 
from yolo.park_other_place import *

# Directory List Declaration
dir_list = ['/home/parking_lot/section1/',
            '/home/parking_lot/section2/',
            '/home/parking_lot/section3/',
            '/home/parking_lot/section4/']


physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
tf.config.experimental.set_memory_growth(physical_devices[0], True)

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    # 첫 번째 GPU에 1GB 메모리만 할당하도록 제한
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)])
    except RuntimeError as e:
        print(e)


CAR_OTHER_PLACE_TIME = time.time()

def carutil_main_func(q1, q2, q3, q4, model_structure_path, model_weight_path, loss='binary_crossentropy', optimizer='adam'):
    global dir_list

    origin1 = []
    origin2 = []
    origin3 = []
    origin4 = []
    while True:
        cur_time = time.time()
        # print(cur_time)
        # print(cur_time-PROCESS_TIME[0],cur_time-PROCESS_TIME[1],cur_time-PROCESS_TIME[2],cur_time-PROCESS_TIME[3])
        origin1 = process_image(q1, 0, cur_time, origin1, model_structure_path, model_weight_path, dir_list)
        time.sleep(1)
        origin2 = process_image(q2, 1, cur_time, origin2, model_structure_path, model_weight_path, dir_list)
        time.sleep(1)
        origin3 = process_image(q3, 2, cur_time, origin3, model_structure_path, model_weight_path, dir_list)
        time.sleep(1)
        origin4 = process_image(q4, 3, cur_time, origin4, model_structure_path, model_weight_path, dir_list)
        time.sleep(1)


if __name__ == '__main__':
    yolo_net, yolo_meta = yolo_model_load(read_cfg='yolov3.cfg',
                                          read_weight='yolov3.weights',
                                          read_data='coco.data')
    pr1 = multiprocessing.Process(target=vi_server1.server1, args=(q1, 'data_section1', 'record_section1', 'server1', 8000))
    pr2 = multiprocessing.Process(target=vi_server2.server2, args=(q2,'data_section2', 'record_section2', 'server2', 8001))
    pr3 = multiprocessing.Process(target=vi_server3.server3, args=(q3,'data_section3', 'record_section3', 'server3', 8002))
    pr4 = multiprocessing.Process(target=vi_server4.server4, args=(q4,'data_section4', 'record_section4', 'server4', 8003))
    pr5 = multiprocessing.Process(target=carutil_main_func, args=(q1, q2, q3, q4, 'car_model_4.json', 'car_model_4.hdf5',))
    pr6 = multiprocessing.Process(target=detection_carplate, args=('car_num.json', 'car_num.h5',))
    pr7 = multiprocessing.Process(target=detection_park_other_place, args=(yolo_net, yolo_meta, dir_list, ))
    pr1.start()
    pr2.start()
    pr3.start()
    pr4.start()
    pr5.start()
    pr6.start()
    pr7.start()