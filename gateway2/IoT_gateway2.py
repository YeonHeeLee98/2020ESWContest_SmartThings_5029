import socket
import threading,time
from multiprocessing import Queue
from car_number_preprocessing import *
import pickle as pkl

s = socket.socket() 
s.bind(('0.0.0.0', 7070)) # 소켓 바인딩
queue = Queue()
s.listen(6) # 최대 수신 값 지정 및 수신 대기

def sending_thread(client_socket, addr):
    global queue
    print('Address :', addr)
    while True:
        while queue.qsize():
            get_data = queue.get()
            print('getting car plate...')
            plate_list, _ = search_image(get_data)
            send_data = {i:plate_list[i] for i in range(len(plate_list))}
            send_data['original_image'] = get_data
            print('end search car plate')
            sending_data = {'car_plate':send_data}
            client_socket.sendall(pkl.dumps((sending_data)))
            print('sending end')
        time.sleep(3)

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
                client_socket.settimeout(10.)
                packet = client_socket.recv(8192)
                if not packet:
                    break 
                data.append(packet)
            except socket.timeout as x:
                break
        if i!=1:
            data = pickle_to_data(data)
            print(data.shape)
            queue.put(data)
            print('data receive end')



while True:
    try:
        clientsocket, address = s.accept() # socket 수락 (통신 중)
        print(address[0], address[1])

        '''
        address[0] : 서버로 수신된 클라이언트 IP
        IoT CCTV, 영상분석영역 간 통신을 위하여
        쓰레드로 구현
        '''
        if address[0] == '210.115.229.72':
            print('image analysis area accept')
            t = threading.Thread(target = sending_thread, args = (clientsocket, address, ))
            t.daemon = True
            t.start()
        else:
            print("IoT CCTV accept")
            t = threading.Thread(target = receiving_thread, args = (clientsocket, address, ))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        s.close()
    except Exception as x:
        print(x)
