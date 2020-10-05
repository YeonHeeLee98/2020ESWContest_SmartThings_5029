import multiprocessing, time, socket
from queue import Queue
import numpy as np
from pprint import pprint
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_update import *
import pickle as pkl
import tensorflow as tf
import socket

#각 주차공간의 주차여부 저장
utilize_list = np.zeros((32), dtype=np.int32)
# Queue Reset
q1, q2, q3, q4 = Queue(), Queue(), Queue(), Queue()
q1.put(True)
q2.put(True)
q3.put(True)
q4.put(True)
#각 주차구역의 주차공간 시작 번호
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

#주차공간별 주차여부 판단을 위한 모델에 입력
#및 전송시점 처리결과를 통한 Queue 제어
'''
SERVER_FLAG : 주차구역 번호
origin : 이전 전처리 이미지
model_structure_path : CNN 기반 모델 구조
model_weight_path : CNN 기반 모델 가중치
idx, img : 해당 주차공간 번호, 해당 주차공간 이미지
predict_output : 주차여부
utilize_list : 각 주차공간의 주차여부 저장
'''
def process_image(idx, img, SERVER_FLAG, model_structure_path, 
                model_weight_path, client_socket, loss='binary_crossentropy', optimizer='adam'):
    global UTILIZE_FLAG
    global utilize_list
    current_time = time.time()
    predict_output = car_observation(img, idx, model_structure_path, model_weight_path)
    update_utilize(predict_output, idx)
    control_process_timing(client_socket, SERVER_FLAG)
    return predict_output


#주차공간 주차여부 갱
'''
utilize_list : 각 주차공간의 주차여부 저장
'''
def update_utilize(predict_output, index):
    global utilize_list
    for idx, output in zip(index, predict_output):
        utilize_list[idx] = output
        print(idx, output)


#주차공간별 주차여부 판단 및 firebase에 전송
'''
input_data : 각 주차공간
imgs_idx : 각 주차공간의 주차번호
model_structure_path : CNN 기반 모델 구조
model_weight_path : CNN 기반 모델 가중치
loaded_model : 학습된 모델 로드
pred : 주차여부
'''
def car_observation(input_data, imgs_idx, model_structure_path, 
                    model_weight_path, loss='binary_crossentropy',
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
    return pred


#주차장 이용률에 따른 전송 시점 조절
'''
predict_output : 주차여부
utilizing_ratio : 주차장 이용률

'''
def control_process_timing(client_socket,SERVER_FLAG):
    global UTILIZE_FLAG
    global utilize_list
    global section_start_num_list
    if SERVER_FLAG < 3:
        predict_output = utilize_list[section_start_num_list[SERVER_FLAG]:section_start_num_list[SERVER_FLAG + 1]]
    else:
        predict_output = utilize_list[section_start_num_list[SERVER_FLAG]:]
    try:
        utilizing_ratio = len(predict_output[predict_output == 1]) / len(predict_output)
    except Exception as x:
        utilizing_ratio = 0
    print('utilizing_ratio =', utilizing_ratio)
    if utilizing_ratio > 0.9:
        UTILIZE_FLAG[SERVER_FLAG] = 0
    elif utilizing_ratio > 0.7:
        UTILIZE_FLAG[SERVER_FLAG] = 1
    elif utilizing_ratio > 0.5:
        UTILIZE_FLAG[SERVER_FLAG] = 2
    else:
        UTILIZE_FLAG[SERVER_FLAG] = 3
    print(UTILIZE_FLAG)
    send_utilize(client_socket)


#IoT Gateway1으로 전송시점 신호 전송
def send_utilize(client_socket):
    global UTILIZE_FLAG
    client_socket.sendall(pkl.dumps((UTILIZE_FLAG)))
    print('UTILIZE_FLAG sending end')
