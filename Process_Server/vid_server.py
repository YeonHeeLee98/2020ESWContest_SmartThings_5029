import io
import socket
import struct
from PIL import Image
import matplotlib.pyplot as pl
import cv2
import numpy as np
from datetime import datetime
import time

'''
images : 모델에 입력될 이미지들 (영상)
total_images : 영상 저장용 이미지들 (영상)
current_day : 현재 날짜(일) >> 하루 치 영상 저장을 위함
video : 비디오 저장을 위한 객체 (입력용)
day_video : 비디오 저장을 위한 객체 (저장용)
'''
def video_server(q,data_section, record_section, server, port):

    #socket 생성 및 바인딩
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(0)

    # 연결 수락
    connection = server_socket.accept()[0].makefile('rb')
    size = (1920,1080) # 해상도 조정
    dtime = datetime.today().strftime('%Y-%m-%d-%H:%M:%S') # 날짜 및 시간 (파일명)
    fname = '/home/parking_lot/' + data_section + '/' + dtime + '.avi' # 저장될 파일 명
    current_day = int(datetime.today().strftime('%d'))

    #비디오 저장을 위한 객체 생성
    video = cv2.VideoWriter(fname,cv2.VideoWriter_fourcc(*'DIVX'), 1, size)
    images = [] # 모델에 입력될 이미지
    total_images = [] # 저장용 이미지
    img = None
    flag = 0
    while True:
        start_time = time.time()
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the
            # length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                break
            image_stream = io.BytesIO() #버퍼
            image_stream.write(connection.read(image_len))
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            image = Image.open(image_stream).convert('RGB') # open image file

            # 사진 저장 
            data = q.get()
            if data:
                print(server, data)
                path = '/home/parking_lot/' + data_section + '/'
                fname = '[' + data_section + ']' + datetime.today().strftime("%Y-%m-%d-%H:%M:%S") + ".jpg"
                image.save(path + fname)
                print('사진 저장 완료')
                q.put(False if data else True)
            else:
                continue
            image = np.array(image)
            cv2.putText(image, datetime.today().strftime("%Y.%m.%d %H:%M:%S"),(1550,1050), 1, 2, 9) # 영상에 현재시간 출력
            images.append(image[...,::-1])
            total_images.append(image[...,::-1])
            if (time.time() - start_time >= 10):
                break
        for i in range(len(images)):
            video.write(images[i])

        #하루 치 영상 저장    
        if (int(datetime.today().strftime('%d')) != current_day):
            fname2 = '/home/parking_lot/' + record_section + '/' + datetime.today().strftime('%Y-%m-%d') + '.avi'
            day_video = cv2.VideoWriter(fname2, cv2.VideoWriter_fourcc(*'DIVX'), 1, size)
            for i in range(len(total_images)):
                day_video.write(total_images[i])
            total_images.clear()
            current_day = int(datetime.today().strftime('%d'))

        dtime = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        fname = '/home/parking_lot/' + data_section + '/' + dtime + '.avi'
        #start_time = time.time()
        images.clear()
        video = cv2.VideoWriter(fname, cv2.VideoWriter_fourcc(*'DIVX'), 1, size)
        day = int(datetime.today().strftime('%d'))
        if (day == 9 or day == 18 or day == 27):
            flag = flag + 1
        if flag == 1:
            os.system('rm  ~/' + data_section + '/*')
        if (day == 10 or day == 19 or day == 28):
            flag = 0
        

    connection.close()
    server_socket.close()
    video.release()
