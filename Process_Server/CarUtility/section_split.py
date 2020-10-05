# -*-coding: utf-8-*-
import pickle as pkl
import cv2
import os
import numpy as np
from os import rename
from cv2_compare import *
from pyspark import SparkContext
#from test3 import *
from queue import Queue
with open('pts.pkl', 'rb') as fr:
    pts_list = pkl.load(fr)

section_start_num_list = [0, 9, 19, 21]

'''
transformation
각 section 별 정해진 좌표 기준으로 자르기 ( 전처리 )
--- 자세히 ---
'''
def partition(section_pts, file_path):
        target_location = np.float32([[0, 0], [0, 150], [150, 0], [150, 150]])
        file_list = [file_path + file_name for file_name in os.listdir(file_path)]
        target_file = sorted(file_list)[-1]
        image = cv2.imread(target_file)
        move_value = cv2.getPerspectiveTransform(section_pts, target_location)
        dst = cv2.warpPerspective(image, move_value, (150, 150))
        return dst

def section(section_flag, dir_path, origin):
    '''
    section_flag : 각 section의 index
    dir_path : section의 이미지 저장 directory
    start_flag : 만약 start_flag == True 면 저장된 origin 없음
    origin : 기존에 있던 이미지 값
    '''

    #분산된 자원 관리를 위한 SparkContext생성
    #클러스터 환경에서 데이터 처리
    sc = SparkContext(master='local[*]') # 분산된 자원 관리를 위한 SparkContext생성
    contrast = []
    global section_start_num_list
    start_flag = False if len(origin) == 0 else True
    section_start_num = section_start_num_list[section_flag]
    cnt =section_flag 
    with open('pts.pkl', 'rb') as fr:
        pts_list = pkl.load(fr)
        
    '''
    코어의 수 만큼 병렬 연산 진행
    rdd : 데이터 분산 (각 코어에 할당)
    section_rdd : 필요한 데이터 형태로 가공(transformation)
    dst : 전처리 과정 연산(transformation) 후 연산된 데이터 가져오기(action)
    '''
    rdd = sc.parallelize(pts_list[section_flag])
    section_rdd = rdd.map(lambda x: (section_flag, x)).groupByKey().mapValues(lambda x: [i for i in x]).\
            filter(lambda x: x[0] == section_flag).flatMap(lambda x: x[1]).map(lambda x: np.float32(x))
    
    dst = section_rdd.map(lambda x: partition(x, dir_path)).collect()
    if not start_flag:
        origin.extend(dst) # if error find here
    else:
        contrast.extend(dst)
    send_image, send_idx, origin, contrast = make_input_image(start_flag, origin, contrast, section_start_num)
    sc.stop()
    return send_image, send_idx, origin

'''
주차 구역별 이미지 비교
---- 자세히 ----
'''
def make_input_image(start_flag, origin, contrast, section_start_num):
    send_image = []
    send_idx = []
    if start_flag:
        compare_output_list = compare(origin, contrast)
        print(type(origin[0].shape), type(contrast[0].shape))
        for i , sending_img in enumerate(compare_output_list):
            if sending_img == True:
                origin[i] = contrast[i]
                send_image.append(contrast[i])
                send_idx.append(i + section_start_num)
            else:
                print(send_idx)
    else:
        send_image = [img for img in origin]
        send_idx = [i + section_start_num for i in range(len(origin))]
    return send_image, send_idx, origin, contrast

