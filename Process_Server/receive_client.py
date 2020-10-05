import socket, datetime
import pickle as pkl
import cv2,time
from multiprocessing import Queue
import threading

#pickle load
def byte2data(data):
	return pkl.loads(b''.join(data))

#dictionary의 key 반환
def getkey(data):
	return list(data.keys())[0]

#데이터 수신 및 데이터 처리 역할에 맞는 pickle dump
def receive_thread(q, socket_name):
	print('thread start')
	while True:
		data = []
		i = 0
		while True:
			try:
				i += 1
				if i == 2:
					print('receive start')
				socket_name.settimeout(2.)
				packet = socket_name.recv(4096)
				if not packet:
					break
				data.append(packet)
			except socket.timeout :
				break
		if i > 2:
			socket_name.sendall('send end'.encode())
			data = byte2data(data)
			key = getkey(data)
			print('data key' , key)
			# time.sleep(1)
			thistime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
			if key == 'yolo':
				q.put(key)
				with open('/home/parking_lot/park_other_place/' + thistime + '.pkl','wb') as f:
					pkl.dump(data[key], f)
			elif key == 'car_plate':
				print(key)
				q.put(key)
				with open('/home/parking_lot/car_plate/' + thistime + '.pkl', 'wb') as f:
					pkl.dump(data[key], f)
			else:
				q.put(key)
				with open('/home/parking_lot/section' + key + '/' + thistime + '.pkl','wb') as f:
					pkl.dump(data[key], f)
			print('file save end')
			print('receive_thread qsize : ',q.qsize())
			print(key)



# if __name__ == '__main__':
# 	receive_thread(frame_queue, s)
