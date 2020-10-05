import multiprocessing
import receive_client
# from queue import Queue
import socket,time,pprint
import os
import numpy as np
import pickle as pkl
import car_observe2
import yolo.park_other_place
from yolo.park_other_place import *
import CarPlate.car_number_model
utilize_list = np.zeros((32), dtype=np.int32)
section_start_num_list = [0, 9, 19, 21]

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect(('IP address', 8080))
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect(('IP address', 7070))
print('connect success')

# 역할별 pickle 데이터 로드 
def read_queue(key):
    if key == 'yolo':
        dirlist = sorted(os.listdir("user's directory"), reverse = True)
        with open("user's directory"+dirlist[0], 'rb') as f:
            output = pkl.load(f)
    elif key == 'car_plate':
        dirlist = sorted(os.listdir("user's directory"), reverse = True)
        with open("user's directory" + dirlist[0], 'rb') as f:
            output = pkl.load(f)
    else:
        dirlist = sorted(os.listdir("user's directory"), reverse = True)
        with open("user's directory"+dirlist[0], 'rb') as f:
            output = pkl.load(f)
    return output # 

#key, value 분리
def split_key_items(dictionary):
    keys = list(dictionary.keys())
    items = np.array(list(dictionary.values()))
    return keys, items
# q에 저장된 키값에 따라 해당 키값에 맞는 함수를 호출 후 스레드로 실행
def read_preprocessed(q, sec_center, sec_img):
    while True:
        print('process size : ',q.qsize())
        if q.qsize():
            key = q.get()
            input_data = read_queue(key)
            # print('process', key)
            if key == 'yolo':
                pr = multiprocessing.Process(target = yolo.park_other_place.detection_park_other_place, args = (yolo_net, yolo_meta, input_data, sec_center, sec_img, ))
                pr.deamon = True
                pr.start()
                print('yolo thread start')
            elif key == 'car_plate':
                pr = multiprocessing.Process(target = CarPlate.car_number_model.detection_carplate, args = (input_data, 'model structure json file', 'model weight file'))
                pr.deamon = True
                pr.start()
                print('car plate search start')
            else:   
                keys,items = split_key_items(input_data)
                pr = multiprocessing.Process(target = car_observe2.process_image, args = (keys, items, int(key)-1, 'model structure json file', 'model weight file', s,))
                pr.deamon = True
                pr.start()
        time.sleep(5)

# read_preprocessed(rq)
if __name__ == '__main__':
    yolo_net, yolo_meta = yolo.park_other_place.yolo_model_load(read_cfg='yolov3.cfg',
                                              read_weight="user's weight file",
                                              read_data="user's data file" )
    rq = multiprocessing.Queue()
    sec_center = multiprocessing.Queue()
    sec_center.put([[],[],[],[]])
    sec_img = multiprocessing.Queue()
    sec_img.put([[], [], [], []])
    pr1 = multiprocessing.Process(target = receive_client.receive_thread, args = (rq, s1, ))
    pr2 = multiprocessing.Process(target = receive_client.receive_thread, args = (rq, s2, ))
    pr3 = multiprocessing.Process(target = read_preprocessed, args = (rq,sec_center, sec_img, ))
    # pr1.deamon = True
    pr2.deamon = True
    pr3.deamon = True
    pr1.start()
    pr2.start()
    pr3.start()
