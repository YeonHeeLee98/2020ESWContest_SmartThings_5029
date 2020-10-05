import sys, os
import yolo.darknet as dn
import pdb
import cv2
import numpy as np
from skimage import measure
import pickle as pkl
import time

def dist(center_0, center_1):
    return np.sqrt((center_0[0]-center_0[0])**2 +  (center_0[0]-center_0[0])**2)

def check_section(img, origin_center, origin_box_img, meta, net):
    cv2.imwrite('./target.jpg', img)
    file_name = './target.jpg'
    bound_box = dn.detect(net, meta, file_name.encode('utf-8'))
    bound_box = np.array(bound_box)
    if len(bound_box) == 0:
        return [], [], 0
    # print(bound_box)
    bound_box = bound_box[:,2]
    new_box_img = []
    new_center = [(int(center_x), int(center_y)) for center_x,center_y,width,height in bound_box]
    for i,box in enumerate(bound_box):
        center_x,center_y,width,height = box
        # print(box)
        if width/2 == float('inf') or center_x - width/2 <= 0 or height/2 == float('inf') or (center_y - height/2) <= 0:
            del new_center[i]
            continue
        min_x = int(center_x - width/2)
        min_y = int(round(center_y) - round(height/2))
        max_x = int(center_x + width/2)
        max_y = int(center_y+height/2)
        new_box_img.append(img[min_y:max_y, min_x: max_x,::])

    illegal_car_count = 0
    if len(origin_center) == 0:
        return new_center, new_box_img, 0
    else:
        for oc in range(len(origin_center)):
            for nc in range(len(new_center)):
                if dist(origin_center[oc], new_center[nc]) < 5:
                    inp = cv2.resize(origin_box_img[oc],dsize = (100,100), interpolation=cv2.INTER_AREA)
                    oup = cv2.resize(new_box_img[nc], dsize = (100,100), interpolation=cv2.INTER_AREA)
                    s = measure.compare_ssim(inp, oup,  multichannel=True)
                    if s > 0.8: 
                        illegal_car_count+=1
    return new_center, new_box_img, illegal_car_count

