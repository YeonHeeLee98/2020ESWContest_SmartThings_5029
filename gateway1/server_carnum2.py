import io
import socket
import threading
from PIL import Image
import pickle as pkl
import cv2
from multiprocessing import Queue
import time
from spark_methods import *
from cv2_compare import *
from pyspark import SparkContext
import numpy as np

'''
section_start_num_list : 각 주차구역의 주차공간 시작번호
origin_img : 유사도 비교를 위한 기존 이미지
queue_db : 로컬 저장소에 쓰레드로 전송하기 위한 queue
queue_pc : 영상분석영역에 쓰레드로 전송하기 위한 queue
time_table : 전송시점을 조절하기 위한 현재 시간 list
'''
section_start_num_list = [0, 9, 19, 21]
origin_img = {}
queue_db = Queue()
queue_pc = {'1': Queue(),
            '2': Queue(),
            '3': Queue(),
            '4': Queue()}
present_time = time.time() # 현재 시간
time_table = [present_time, present_time, present_time, present_time]
del present_time

'''
전송 시점 :
10초/180초/300초/600초에 한번씩 전송
전송 시점이 길어질수록 주차장 여유
'''
TIME_FLAG = [10, 180, 300, 600]
# Sections's Flag Declaration
UTILIZE_FLAG = [0, 3, 3, 3]
yolo_timer = time.time() # yolo 전송시점을 위한 현재 시간 저장

'''
s : IoT CCTV 및 서버와의 통신을 위한 소켓 생성
sc : spark 클러스터 접근
'''
s = socket.socket()
s.bind(('0.0.0.0',8080)) # 소켓 바인딩
s.listen(6) # 최대 수신 값 지정 및 수신 대기
sc = SparkContext(master='local[*]')

#pts_list : 각 주차구역 분할을 위한 좌표 데이터
with open('pts.pkl', 'rb') as fr:
    pts_list = pkl.load(fr)


# 영상분석영역 전송 시점 조절
def control_send2pc_time():
    global TIME_FLAG
    global time_table
    global UTILIZE_FLAG
    i = 0
    check_section = []
    print(time_table)
    for section_time in time_table:
        if (time.time() - section_time ) > TIME_FLAG[UTILIZE_FLAG[i]]:
            time_table[i] = time.time() # time_table 초기화
            check_section.append(i)
        print(int(time.time() - section_time), TIME_FLAG[UTILIZE_FLAG[i]])
        print('{} section need to send?'.format(i+1), (time.time() - section_time) > TIME_FLAG[UTILIZE_FLAG[i]])
        i+=1
    print('send section number', check_section)
    return check_section


# 전처리된 데이터 간 유사도 비교
'''
section_number : 주차구역 번호
processed_value :전처리된 데이터
start_num : 주차공간 시작 번호
end_num : 주차공간 끝번호
send_value : 각 주차공간 간 유사도 변화가 있는 데이터
'''
def get_preprocess(section_number, processed_value):
    global origin_img
    start_num = section_start_num_list[section_number]
    end_num = section_start_num_list[section_number+1] if section_number != 3 else 32
    print(start_num, end_num)
    print('mapping value : ',len(processed_value))
    print([False if i in origin_img else True for i in range(start_num, end_num)])
    send_value = {}
    if not all([False if i in origin_img else True for i in range(start_num, end_num)]):
        compare_img_list = [origin_img[i] for i in range(start_num, end_num)]
        sim_list = compare(compare_img_list, processed_value)
        for i in range(start_num, end_num):
            if sim_list[i-start_num]:
                origin_img[i] = processed_value[i-start_num]
                send_value[i] = processed_value[i-start_num]
    else:
        for i in range(start_num, end_num):
            origin_img[i] = processed_value[i-start_num]
            send_value[i] = processed_value[i-start_num]
    print('Need to analysis car number :', send_value.keys())
    return send_value


#주차구역 이외공간 전처리 및 해당 데이터 yolo에 전송
'''
yolo_timer : 전송 시점을 위한 현재시간
send_value : 전처리된 데이터

'''
def yolo_send(client_socket):
    global pts_list
    global queue_pc
    global yolo_timer
    if (time.time() - yolo_timer) > 600:
        yolo_timer = time.time()
        send_value = []
        for i,key,flag in zip(range(4),['1','2','3','4'],[2,3,2,4]):
            img = queue_pc[key].get()
            queue_pc[key].put(img)
            send_value.append(make_dark_box(img, pts_list[i], flag))
        send_value = ({'yolo':send_value})
        client_socket.sendall(pkl.dumps(send_value))
        good = client_socket.recv(4096)
        print(good.decode(), 'sending pc','n')
    else:
        return


#Spark를 이용한 주차구역 전처리 및 해당 데이터 영상분석영역에 전송
'''
section_num_list : 전처리할 구역 번호
key : 주차구역 번호
sending_data : 전처리할 주차구역 프레임
processed_value : 전처리된 데이터

'''
def send2pc_thread(client_socket, addr):
    global queue_pc
    print('Address :', addr)
    while True:
        # yolo_send(client_socket)
        section_num_list = control_send2pc_time()
        for section_number in section_num_list:
            key = str(section_number+1)
            sending_data = queue_pc[key].get()
            print('send start!!!', end = '\t')
            print('sended section number', key)
            processed_value = do_spark(section_number = section_number,
                                       img = sending_data,
                                       pts_list = pts_list,
                                       spark_context =  sc)
            send_value = get_preprocess(section_number, processed_value)
            send_value = ({str(section_number+1):send_value})
            client_socket.sendall(pkl.dumps(send_value))
            print('send end')
            client_socket.settimeout(10.)
            good = client_socket.recv(4096)
            print(good.decode())
        print('send the data for car utilize analysis')
        print('queue empty five seconds sleep...')
        time.sleep(5)


#데이터 수신
def receive_pc(client_socket, addr):
    global UTILIZE_FLAG
    print("receive pc thread start")
    while True:
        data = []
        i=0
        while True:
            try:
                client_socket.settimeout(2.)
                packet = client_socket.recv(4096)
                print(i, len(packet))
                if not packet:
                    break 
                data.append(packet)
            except socket.timeout as x:
                break
        try:
            data = pkl.loads(b''.join(data))
            if len(data) != []:
                UTILIZE_FLAG=data
            print('UTILIZE_FLAG update')
        except Exception as x:
            continue


#영상의 프레임을 로컬 저장소에 저장
def send2db_thread(client_socket, addr):
    global queue_db
    print('Address :', addr)
    while True:
        while queue_db.qsize():
            get_data = queue.get() # 영상 프레임
            print('send to local Data Base')
            client_socket.sendall(pkl.dumps(send_values))
            print('send end')
            good = client_socket.recv(4096)
            print(good.decode())
        print('present q size is zero sleep five seconds')
        time.sleep(5)

#pickle load
def pickle_to_data(binary_data):
    return pkl.loads(b"".join(binary_data))


#IoT CCTV로부터 데이터 수신
'''
data : IoT CCTV로부터 수신된 데이터
packet : 패킷 단위 데이터 수신
'''
def receiving_thread(client_socket, addr):
    global queue
    print("Address :", addr)
    print('data receive start')

    while True:
        data = []
        i=0
        while True:
            try:
                i+=1
                if i==2:
                    print('socket receiving...')
                client_socket.settimeout(2.)
                packet = client_socket.recv(2048)
                # print(i, len(packet))
                if not packet:
                    break 
                data.append(packet)
            except socket.timeout as x:
                break
        if i!=1:
            data = pickle_to_data(data)
            # queue_db.put(data)
            if queue_pc[get_key(data)].qsize():
                _ = queue_pc[get_key(data)].get()
            queue_pc[get_key(data)].put(data[get_key(data)])
            
            print(get_key(data), 'queue received new data')
            print('data receive end')
        client_socket.send('send over'.encode())

while True:
    try:
        clientsocket, address = s.accept() # socket 수락 (통신 중)
        print(address[0], address[1])
        
        '''
        address[0] : 서버로 수신된 클라이언트 IP
        IoT CCTV, 로컬 저장소, 영상분석영역 간 통신을 위하여
        쓰레드로 구현
        '''
        if address[0] == '10.50.231.97':
            print('local db accept')
            t = threading.Thread(target = send2db_thread, args = (clientsocket, address, ))
            t.daemon = True
            t.start()
        elif address[0] == '210.115.229.72':
            print('analysis server accept')
            t1 = threading.Thread(target = send2pc_thread, args = (clientsocket, address, ))
            t2 = threading.Thread(target = receive_pc, args = (clientsocket, address, ))
            t1.daemon = True
            t1.start()
            t2.daemon = True
            t2.start()
        else:
            print("IoT CCTV accept")
            t = threading.Thread(target = receiving_thread, args = (clientsocket, address, ))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        s.close()
    except Exception as x:
        print(x)

s.close()
clientsocket.close()
sc.stop()
