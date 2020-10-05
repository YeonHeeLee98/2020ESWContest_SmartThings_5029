import sys, os
# import yolo.darknet as dn
import pdb
import cv2
import numpy as np
from skimage import measure
import pickle as pkl
import time
from pprint import pprint
# 이미지에서 지정된 구역을  검은 박스로 칠함
def dark_box(img, pts):
    side_point = pts[0][0], pts[0][1], pts[-1][2], pts[-1][3]
    min_x = min(side_point[0][1], side_point[1][1])
    min_y =  min(side_point[0][0], side_point[1][0])
    max_x = max(side_point[2][1],side_point[3][1])
    max_y = max(side_point[1][0],side_point[2][0])
    cv2.rectangle(img, (min_y, min_x), (max_y, max_x), (0,0,0), -1)
    return img
# 이미지에서 주차위치에 따라 구분하여 dark_box함수를 통해 지정 구역을 제거
def make_dark_box(img, pts, side_flag):
    up_side = pts[:side_flag]
    if len(pts)-side_flag == 0:
        dark_box(img, up_side)
    else:
        down_side = [pts[side_flag],pts[-1]]
        img = dark_box(img, up_side)
        img = dark_box(img, down_side)
    print('yolo preprocess an image')
    return img
