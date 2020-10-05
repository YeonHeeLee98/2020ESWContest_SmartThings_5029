import cv2
import numpy as np
import pickle as pkl
import time
import os
from firebase_update import *

def detection_carplate(receive_file, model_structure_path, model_weight_path, loss='sparse_categorical_crossentropy',
                       optimizer='adam'):
    with open('dic_to_char.pkl', 'rb') as f:
        num_to_char = pkl.load(f)
    origin_img = receive_file.pop('original_image')
    keys = list(receive_file.keys())
    if len(keys) == 0 :
        return
    else:
        car_plate_detection(receive_file, 
                            num_to_char, 
                            model_structure_path, 
                            model_weight_path, 
                            loss, 
                            optimizer,
                            img_shape = (200, 50))
    print('car plate processing end')


# 번호판 OCR을 수행하기 위한 함수
def car_plate_detection(receive_file, to_char_dic, model_structure_path, model_weight_path, loss, optimizer,
                        img_shape=(200, 50)):
    try:
        from keras.models import model_from_json
        import keras.backend as K
        K.clear_session()
        with open(model_structure_path, 'r') as model:
            loaded_model = model.read()
        loaded_model = model_from_json(loaded_model)
        loaded_model.load_weights(model_weight_path)
        loaded_model.compile(loss=loss, optimizer=optimizer)

        keys = list(receive_file.keys())
        plate_list = []
        for i in keys:
            step_img = cv2.resize(receive_file[i], img_shape, interpolation=cv2.INTER_AREA)
            step_img = np.reshape(step_img, (200, 50, 1))
            step_img = step_img.astype(np.float32)
            print(i, step_img.shape)
            step_img = (step_img / 255.).astype(np.float32)
            plate_list.append(step_img)
        if len(plate_list) == 0:
            return

        plate_list = np.reshape(plate_list, (-1, 200, 50, 1))
        predict = loaded_model.predict(plate_list)
        predict_output = []
        for plate in predict:
            idx = np.argmax(plate, axis=-1)
            c = ''
            for index in idx:
                if to_char_dic[index] == 'pad':
                    continue
                c += to_char_dic[index]
            predict_output.append(''.join(c).strip())
        # print(predict_output)
    except Exception as x:
        print(x)
        time.sleep(10)
        car_plate_detection(img_file, to_char_dic, model_structure_path, model_weight_path, loss, optimizer,
                            img_shape=(200, 50))
    print('predict output :', predict_output)
    return predict_output
