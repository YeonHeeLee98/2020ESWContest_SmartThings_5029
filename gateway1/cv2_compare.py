from skimage import measure
import matplotlib.pyplot as plt
import numpy as np
import cv2
from time import sleep

'''
같은 주차공간에서 현재 이미지와
이전 이미지의 유사도를 비교

s : 두 이미지의 유사도
'''
def compare_images(imageA, imageB):
        
    # compute the tructural similarity
    s = measure.compare_ssim(imageA, imageB,  multichannel=True)
    print("Similarity: %.2f" % s)
    print(s)
    return s


#유사도 비교를 통한 결과(True,False) 전송
'''
sim_list : 각 주차공간에서 변화가 있으면 True, 변화가 없으면 False
original : 이전 이미지
contrast : 비교 대상이 되는 현재 이미지
'''
def compare(origImg, contImg) : 
    sim_list = []
    for i in range(len(origImg)) :
        original = origImg[i]
        contrast = contImg[i]

        sim = compare_images(original, contrast)
        if(sim <= 0.7):
            sim_list.append(True)
        else:
            sim_list.append(False)

        # sleep(0.5)

    return sim_list
        


