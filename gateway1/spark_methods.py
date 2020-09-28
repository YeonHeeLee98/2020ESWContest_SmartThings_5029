import numpy as np
import cv2


#주차공간 추출을 위한 병렬연산
'''
section_pts : 해당 주차구역의 분할을 위한 좌표
target_location : 원근법 변환에 대한 목표 위치
move_value : 기울어진 주차공간 원근법 변환
dst : 분할된 주차구역(주차공간)
'''
def prep(section_pts,img):
    target_location = np.float32([[0,0],[0,150],[150,0],[150,150]])
    move_value = cv2.getPerspectiveTransform(section_pts,target_location)
    dst = cv2.warpPerspective(img, move_value, (150,150))
    return dst


#Spark를 활용한 전처리 과정 병렬연산
'''
rdd : 데이터 분산 (각 코어에 할당)
section_rdd : 필요한 데이터 형태로 가공(Transformation)
dst ; 전처리 과정 연산(Transformation) 후 연산된 데이터 가져오기(Action)
'''
def do_spark(section_number, img, pts_list,spark_context):
    rdd = spark_context.parallelize(pts_list[section_number])
    section_rdd = rdd.map(lambda x: (section_number, x)).groupByKey().mapValues(lambda x: [i for i in x]).\
            filter(lambda x: x[0] == section_number).flatMap(lambda x: x[1]).map(lambda x: np.float32(x))
    dst = section_rdd.map(lambda x: prep(x, img)).collect()
    return dst

#key(주차공간 번호) 반환
def get_key(dict):
    return list(dict.keys())[0]
