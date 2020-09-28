import socket, time
import pickle as pkl
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera 
from multiprocessing import Queue
import threading

'''
camera_name : 주차구역별 카메라 번호
camera : 라즈베리파이 카메라 모듈사용을 위한 객체
rawCapture : 촬영 이미지의 데이터 타입을 Numpy Array로 다루기 위한 객체
'''
camera_name = '1'
camera = PiCamera()
camera.vflip = True
camera.resolution = (1920, 1080) # 해상도설정
camera.framerate = 32
rawCapture = PiRGBArray(camera, size = (1920, 1080))

'''
frame_queue : 쓰레드 동작을 위한 queue
s : IoT Gateway와 통신을 위한 소켓 생성
'''
time.sleep(0.1)
frame_queue = Queue()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('210.115.227.119', 8080)) # IoT Gateway와 연결요청


# 주차구역 촬영
'''
image : Numpy Array 타입 이미지 (촬영된 프레임)
'''
def video_camera(camera, capture):
   global frame_queue
   for frame in camera.capture_continuous(rawCapture, format = 'bgr', use_video_port = True):
      image = frame.array
      key = cv2.waitKey(1)
      frame_queue.put(image)
      print('frame queue size : ', frame_queue.qsize())
      rawCapture.truncate(0)

      if key == ord("q"):
         break
      time.sleep(10)

# IoT Gateway로 프레임 및 이미지 전송
'''
img : Numpy Array 타입 이미지 (촬영된 프레임)
'''
def sending_thread(client_socket):
   global frame_queue
   while True:
      try:
         while frame_queue.qsize():
            img = frame_queue.get()
            print('img sending start')
            client_socket.sendall(pkl.dumps(({camera_name:img})))
            print('img sending end')
            data = client_socket.recv(4069)
            print(data.decode())            
      except KeyboardInterrupt:
         client_socket.close()


# 주차구역 촬영 및 전송을 쓰레드로 구현
t1 = threading.Thread(target = video_camera, args=(camera, rawCapture,))
t2 = threading.Thread(target = sending_thread, args=(s,))
t1.deamon = True
t2.deamon = True

t1.start()
t2.start()
