# 2020ESWContest_SmartThings_5029

<p align="center"><img src="./img/주차의민족.png" width="200" style="border-radius:10%"></p>
<h1 align="center"> ParkingScanner </h1>


## 개요

2020 임베디드 소프트웨어 경진대회 'Smart Things' 부문 주차의 민족 팀입니다.

## 시스템 개요 

- 본 작품은 주차장을 실시간으로 통합 관리하기 위한 시스템이다. 해당 작품은 IoT(Internet of Things) CCTV를 통해 주차장 촬영을 수행하며 전송된 영상을 실시간 영상 분석을 통해 분석된 결과를 사용자와 관리자에게 제공한다. 사용자는 해당 시스템으로부터 주차장 이용률, 각 주차공간별 주차 여부 및 주차장의 정보를 제공받는다. 또한 관리자는 주차장의 이용률 및 주차장의 불법주차 여부를 제공받는다. 이를 통해 관리자는 주차장을 효율적으로 관리하며, 주차장 사용자에게는 보다 질 높은 서비스를 제공한다.

## 시스템 구조


## 개발 환경 


## 디렉토리 구조
```
 ├── _Android  
 │   ├── _.idea  
 │   ├── _app
 │   │   ├── _libs
 │   │   ├── _src
 │   │   │   ├── _androidTest/java/com/example/Smart_Parking_System
 │   │   │   ├── _test/java/com/example/Smart_Parking_System
 │   │   │   └── _main
 │   │   │       ├── _java/com/example/Smart_Parking_System
 │   │   │       ├── Car.java
 │   │   │       │   ├── CarAdapter.java
 │   │   │       │   ├── MainActivity.java
 │   │   │       │   └── ParkingLotActivity.java
 │   │   │       ├── _res
 │   │   │       │   ├── _layout
 │   │   │       │   │   ├── activity_main.xml
 │   │   │       │   │   ├── activity_parking_lot.xml
 │   │   │       │   │   └── car_item.xml
 │   │   │       │   └── ...
 │   │   │       └── ... 
 │   │   └── ...
 │   └── ... 
 │
 ├── _Web  
 │   ├── _public
 │   │   ├── app.js
 │   │   ├── config.js
 │   │   ├── firebase-messaging-sw.js
 │   │   └── index.html
 │   │
 │   ├── database.rules.json
 │   ├── firebase.json
 │   └── package-lock.json
 │
 ├── _Process_Server  
 │   ├── _CarPlate 
 │   │   ├── car_number_model.py
 │   │   └── car_number_preprocessing.py
 │   ├── _CarUtility
 │   │   ├── car_obs.py
 │   │   └── new_section_split2.py
 │   ├── _yolo
 │   │   ├── darknet.py
 │   │   ├── park_other_place.py
 │   │   └── yolo_methods.py
 │   │
 │   ├── cv2_compare.py 
 │   ├── firebase_test.py
 │   ├── main.py
 │   ├── measure_img_similarity.py
 │   └── vid_server.py
 │
 └── README.md  
 ```

## 팀

- 팀명 : 주차의 민족
- 팀원
  - 정영석 / dnfkdi1995@gmail.com
  - 이연희 / yhlee98y@gmail.com
  - 노재영 / groove38@naver.com
  - 손주형 / jhson722@naver.com
  - 김도경 / jes1456@naver.com



