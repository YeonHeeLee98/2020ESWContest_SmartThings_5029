import cv2
import numpy as np
import pickle as pkl
from car_number_preprocessing import *
import time
import os
from firebase_test import *

CAR_PLATE_TIME = time.time()

def detection_carplate(model_structure_path, model_weight_path, loss='sparse_categorical_crossentropy',
                       optimizer='adam', cur_time=CAR_PLATE_TIME):
    with open('dic_to_char.pkl', 'rb') as f:
        num_to_char = pkl.load(f)
    while True:
        if time.time() - cur_time > 600:
            file_name = ['/home/parking_lot/car_plate/' + name for name in os.listdir('/home/parking_lot/car_plate') if
                         name[-3:] == 'jpg']
            # print(sorted(file_name)[-1])
            file_name = sorted(file_name)[-1]
            predict = car_plate_detection(file_name, num_to_char, model_structure_path, model_weight_path, loss,
                                          optimizer)
            if predict != 0:
                for pred in predict:
                    fire_base_carnum(predict)
                    fileUpload(file_name, pred)
            cur_time = time.time()

        else:
            print(time.time() - cur_time)
            time.sleep(300)
            continue


def car_plate_detection(img_file, to_char_dic, model_structure_path, model_weight_path, loss, optimizer,
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

        plate_list, _ = search_image(img_file)
        for i in range(len(plate_list)):
            step_img = cv2.resize(plate_list[i], img_shape, interpolation=cv2.INTER_AREA)
            step_img = np.reshape(step_img, (200, 50, 1))
            step_img = step_img.astype(np.float32)
            step_img = (step_img / 255.).astype(np.float32)
            plate_list[i] = step_img

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
    except:
        time.sleep(10)
        car_plate_detection(img_file, to_char_dic, model_structure_path, model_weight_path, loss, optimizer,
                            img_shape=(200, 50))
    return predict_output
