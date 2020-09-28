import cv2
import numpy as np
import matplotlib.pyplot as plt

MAX_DIAG_MULTIPLYER = 5 # 5 대각선 길이의 5배 안에 있는가
MAX_ANGLE_DIFF = 10.0 # 12.0 앵글 값
MAX_AREA_DIFF = 0.5 # 0.5
MAX_WIDTH_DIFF = 0.8 # 컨투어 사이 너비차이
MAX_HEIGHT_DIFF = 0.2 # 컨투어 사이 높이 차이
MIN_N_MATCHED = 5 # 번호판 으로 인정하는 최소 글자(?)

#이미지 블러링
'''
img_blurred_med : 메디안 블러링 적용된 이미지
img_thresh : Thresholding 된 이미지 (구역별 이진화)
'''
def blurring_image(img_data):
	img_blurred_med = cv2.medianBlur(img_data, 9)
	# using median filter for remove noise
	
	img_thresh = cv2.adaptiveThreshold(img_blurred_med,
									   maxValue = 255.0,
									   adaptiveMethod = cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       thresholdType = cv2.THRESH_BINARY_INV,
                                       blockSize = 19,
                                       C = 9
                                       )
	# if pixel value is lower than threshold value. the value is exchange 0

	return img_thresh

#이미지 윤곽 찾기
'''
height, width, channel : 이미지의 너비, 높이, 채널(RGB)
contours_dict : 윤곽선
contours : 전체 이미지의 윤곽 찾기
x,y,w,h : 직사각형 꼭지점 및 폭
'''
def finding_contours(threshed_img, img_shape):
	height, width, channel = img_shape
	contours_dict = []

	contours, _ = cv2.findContours(threshed_img,
                                mode = cv2.RETR_LIST,
                                method = cv2.CHAIN_APPROX_SIMPLE)
	# finding contours
	for contour in contours:
	    x,y,w,h = cv2.boundingRect(contour)
	    
	    contours_dict.append({
	        'contour':contour,
	        'x':x,
	        'y':y,
	        'w':w,
	        'h':h,
	        'cx':x + (w/2),
	        'cy':y+ (h/2)
	    })
	# save the Rectengle size for making contour's Rectangle  
	return contours, contours_dict


# 윤곽선 노이즈 제거
'''
possible_contours : 노이즈 제거 후 윤곽선
'''
def removing_noise_contour(contours_dict):
	MIN_AREA = 300 # minimum Rectangle size
	MIN_WIDTH, MIN_HEIGHT = 1,4 # minimum width and height size
	#  small size Rectangle will  
	MIN_RATIO, MAX_RATIO = 0.25, 1.5
	possible_contours = []
	cnt = 0
	for d in contours_dict:
	    area = d['w'] * d['h']
	    ratio = d['w'] / d['h']
	    if area > MIN_AREA and d['w'] > MIN_WIDTH and d['h'] > MIN_HEIGHT and MIN_RATIO < ratio < MAX_RATIO:
	        d['idx'] = cnt
	        cnt += 1
	        possible_contours.append(d)
	return possible_contours


def find_chars(contour_list, possible_contours):
    matched_result_idx = []
    
    for d1 in contour_list:
        matched_contours_idx = []
        
        for d2 in contour_list:
            if d1['idx'] == d2['idx']:
                continue
            dx = abs(d1['cx'] - d2['cx'])
            dy = abs(d1['cy'] - d2['cy'])
            
            diagonal_length = np.sqrt(d1['w'] ** 2 + d1['h'] ** 2)
            
            distance = np.linalg.norm(np.array([d1['cx'], d1['cy']]) - np.array([d2['cx'], d2['cy']]))
            
            if dx == 0:
                angle_diff = 90
            else:
                angle_diff = np.degrees(np.arctan(dy/dx))
            area_diff = abs(d1['w'] * d1['h'] - d2['w'] * d2['h'])/(d1['w'] * d1['h'])
            width_diff = abs(d1['w'] - d2['w']) / d1['w']
            height_diff = abs(d1['h'] - d2['h'])/d1['h']
            
            if distance < diagonal_length * MAX_DIAG_MULTIPLYER \
            and angle_diff < MAX_ANGLE_DIFF and area_diff < MAX_AREA_DIFF \
            and width_diff < MAX_WIDTH_DIFF and height_diff < MAX_HEIGHT_DIFF:
                matched_contours_idx.append(d2['idx'])
            
        matched_contours_idx.append(d1['idx'])
        
        if len(matched_contours_idx) < MIN_N_MATCHED:
            continue
        matched_result_idx.append(matched_contours_idx)
        unmatched_contour_idx = []
        
        for d4 in contour_list:
            if d4['idx'] not in matched_contours_idx:
                unmatched_contour_idx.append(d4['idx'])
        
        unmatched_contour = np.take(possible_contours, unmatched_contour_idx)
        
        recursive_contour_list = find_chars(unmatched_contour,possible_contours)
        for idx in recursive_contour_list:
            matched_result_idx.append(idx)
        break
    return matched_result_idx

def car_number_result(matched_result,img_thresh, img_shape):
	PLATE_WIDTH_PADDING = 1.1 # 1.3
	PLATE_HEIGHT_PADDING = 1.47 # 1.5
	MIN_PLATE_RATIO = 3
	MAX_PLATE_RATIO = 10

	plate_imgs = []
	plate_infos = []
	height, width, channel = img_shape
	for i, matched_chars in enumerate(matched_result):
	    sorted_chars = sorted(matched_chars, key=lambda x: x['cx'])

	    plate_cx = (sorted_chars[0]['cx'] + sorted_chars[-1]['cx']) / 2
	    plate_cy = (sorted_chars[0]['cy'] + sorted_chars[-1]['cy']) / 2
	    
	    plate_width = (sorted_chars[-1]['x'] + sorted_chars[-1]['w'] - sorted_chars[0]['x']) * PLATE_WIDTH_PADDING
	    
	    sum_height = 0
	    for d in sorted_chars:
	        sum_height += d['h']

	    plate_height = int(sum_height / len(sorted_chars) * PLATE_HEIGHT_PADDING)
	    
	    triangle_height = sorted_chars[-1]['cy'] - sorted_chars[0]['cy']
	    triangle_hypotenus = np.linalg.norm(
	        np.array([sorted_chars[0]['cx'], sorted_chars[0]['cy']]) - 
	        np.array([sorted_chars[-1]['cx'], sorted_chars[-1]['cy']])
	    )
	    
	    angle = np.degrees(np.arcsin(triangle_height / triangle_hypotenus))
	    
	    rotation_matrix = cv2.getRotationMatrix2D(center=(plate_cx, plate_cy), angle=angle, scale=1.0)
	    
	    img_rotated = cv2.warpAffine(img_thresh, M=rotation_matrix, dsize=(img_shape[1], img_shape[0]))
	    
	    img_cropped = cv2.getRectSubPix(
	        img_rotated, 
	        patchSize=(int(plate_width), int(plate_height)), 
	        center=(int(plate_cx), int(plate_cy))
	    )
	    
	    if img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO or img_cropped.shape[1] / img_cropped.shape[0] < MIN_PLATE_RATIO > MAX_PLATE_RATIO:
	        continue
	    
	    plate_imgs.append(img_cropped)
	    plate_infos.append({
	        'x': int(plate_cx - plate_width / 2),
	        'y': int(plate_cy - plate_height / 2),
	        'w': int(plate_width),
	        'h': int(plate_height)
	    })
	    
	return plate_imgs,plate_infos

#이미지 탐색
'''
img_shape : 이미지의 shape
gray_img : 흑백으로 변환된 이미지
blur_image : 흑백 이미지에서 블러링된 이미지
.
.

'''
def search_image(img):
	img_shape = img.shape
	gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	blur_image = blurring_image(gray_img)
	contour, contour_dict = finding_contours(blur_image, img_shape)
	possible_contours = removing_noise_contour(contour_dict)
	result_idx = find_chars(possible_contours, possible_contours)
	matched_result = []
	for idx_list in result_idx:
	    matched_result.append(np.take(possible_contours, idx_list))

	plate_list,plate_infos = car_number_result(matched_result,blur_image,img_shape)
	return plate_list, plate_infos
