import time
import multiprocessing
from queue import Queue
import cv2
import os
import numpy as np
from pprint import pprint
import CarUtility.section_split as section_split
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_update import *
from CarPlate.car_number_preprocessing import *
import yolo.darknet as dn
import pickle as pkl
from yolo import *
import tensorflow as tf




utilize_list = np.zeros((32), dtype=np.int32)
# Queue Reset
q1, q2, q3, q4 = Queue(), Queue(), Queue(), Queue()
q1.put(True)
q2.put(True)
q3.put(True)
q4.put(True)
section_start_num_list = [0, 9, 19, 21]
# Define Time Flag
TIME_FLAG = [10, 180, 300, 600]
# Sections's Flag Declaration
UTILIZE_FLAG = [0, 0, 0, 0]
# Start Process Time
PROCESS_TIME = [time.time(), time.time(),
                time.time(), time.time()]

'''
4가지 기준으로 구분하여 업데이트 시간 조절

이용률에 따라 UTILIZE_FLAG 0,1,2,3구분

이용률에 따른 시간을 TIME_FLAG로 지정
'''
sec_center = [[], [], [], []]
sec_img = [[], [], [], []]


def process_image(q, SERVER_FLAG, origin, model_structure_path, model_weight_path, dir_list, 
                  loss='binary_crossentropy', optimizer='adam'):
    global UTILIZE_FLAG
    global utilize_list
    value = q.get()
    current_time = time.time()
    if value:
        img, idx, origin = section_split.section(SERVER_FLAG, dir_list[SERVER_FLAG],
                                                      origin)
        if len(img) == 0:
            q.put(False)
            return origin
        predict_output = car_observation(img, idx, model_structure_path, model_weight_path)

        for idx_value, pred in zip(idx, predict_output):
            utilize_list[idx_value] = pred
        control_process_timing(utilize_list, SERVER_FLAG)
        # print(utilize_list)
        q.put(False)
    elif (current_time - PROCESS_TIME[SERVER_FLAG]) > TIME_FLAG[UTILIZE_FLAG[SERVER_FLAG]]:
        PROCESS_TIME[SERVER_FLAG] = time.time()
        q.put(True)
    else:
        q.put(False)
        time.sleep(1)
    return origin


def car_observation(input_data, imgs_idx, model_structure_path, model_weight_path, loss='binary_crossentropy',
                    optimizer='adam'):
    from keras.models import model_from_json
    import keras.backend as K
    K.clear_session()
    with open(model_structure_path, 'r') as model:
        loaded_model = model.read()
    loaded_model = model_from_json(loaded_model)
    loaded_model.load_weights(model_weight_path)
    loaded_model.compile(loss='binary_crossentropy', optimizer='adam')

    input_data = np.array(input_data).reshape(-1, 150, 150, 3)
    pred = np.array(loaded_model.predict(input_data))
    # pred = np.argmax(pred, axis = 1)
    pred = list(pred.argmax(axis=1))
    # 수정 필요'0-
    firebase_update(imgs_idx, pred)
    return pred

def control_process_timing(predict_output, SERVER_FLAG):
    global UTILIZE_FLAG
    global section_start_num_list
    predict_output = np.array(predict_output)
    if SERVER_FLAG < 3:
        predict_output = predict_output[section_start_num_list[SERVER_FLAG]:section_start_num_list[SERVER_FLAG + 1]]
    else:
        predict_output = predict_output[section_start_num_list[SERVER_FLAG]:]
    try:
        utilizing_ratio = len(predict_output[predict_output == 1]) / len(predict_output)

    except Exception as x:
        utilizing_ratio = 0

    if utilizing_ratio > 0.9:
        UTILIZE_FLAG[SERVER_FLAG] = 0
    elif utilizing_ratio > 0.7:
        UTILIZE_FLAG[SERVER_FLAG] = 1
    elif utilizing_ratio > 0.5:
        UTILIZE_FLAG[SERVER_FLAG] = 2
    else:
        UTILIZE_FLAG[SERVER_FLAG] = 3