
<p align="center"><img src="./img/주차의민족.png" width="400" style="border-radius:10%"></p>
<h1 align="center"> ParkingScanner </h1>


## 개요

2020 임베디드 소프트웨어 경진대회 'Smart Things' 부문 주차의 민족 팀

## 시스템 개요 

  본 시스템은 주차장을 실시간으로 통합 관리하기 위한 시스템이다. 해당 작품은 IoT(Internet of Things) CCTV를 통해 주차장 촬영을 수행하며 전송된 영상을 실시간 영상 분석을 통해 분석된 결과를 사용자와 관리자에게 제공한다. 사용자는 해당 시스템으로부터 주차장 이용률, 각 주차공간별 주차 여부 및 주차장의 정보를 제공받는다. 또한 관리자는 주차장의 이용률 및 주차장의 불법주차 여부를 제공받는다. 이를 통해 관리자는 주차장을 효율적으로 관리하며, 주차장 사용자에게는 보다 질 높은 서비스를 제공한다.

1. IoT CCTV 영역
    - IoT CCTV 기반의 실시간 영상 전송 시스템
        - IoT CCTV는 주차장의 주차공간 촬영을 수행하며, Wi-Fi 무선 근거리 통신망을 통해 영상처리 영역으로 실시간으로 전송이 가능
2. 영상처리 영역
    - 잔여 주차공간을 고려한 영상의 분석 시점 조절 알고리즘
        - 한정된 서버 자원을 효율적으로 사용하기 위한 영상 분석의 시점을 조절하는 알고리즘
    - 병렬 연산을 통한 효율적 영상처리 알고리즘 
        - 시스템의 중요한 요소인 실시간성 보장을 위해 병렬 연산을 통해 데이터의 전처리를 수행하는 효율적인 영상처리 알고리즘
    - 딥러닝 모델의 효율성 증대를 위한 입력 프레임간 유사도 비교
        - 딥러닝 모델에 입력되는 영상의 입력 프레임간 유사도 비교를 통해 딥러닝 모델의 효율성을 증대하기 위한 입력 프레임간 유사도 비교 알고리즘 
    - CNN 기반의 주차공간별 주차 여부 판단을 위한 딥러닝 모델 
        - 주차공간별로 주차 여부를 판단하기 위해 딥러닝 모델. 모델은 이미지 처리에 뛰어난 성능을 보이는 CNN(Convolutional Neural Network) 기반으로 구현
    - 특별주차구역 불법주차 차량의 번호판 인식 알고리즘 개발
        - 특별주차구역이란 특정 주차 대상이 지정되어 있는 공간을 의미
        - 해당 구역의 불법주차 차량 검출을 위해 번호판 검출 및 인식 알고리즘
    - 주차구역 이외 공간의 불법주차 차량 검출을 위한 YOLO 기반의 딥러닝 모델
        - 주차장의 혼잡도를 낮추고 정해진 주차구역 이외의 공간에 주차된 차량을 탐지하기 위해 불법주차 차량 검출 모델
        - 불법주차 차량 검출 모델은 YOLO(You Only Look Once) 알고리즘을 이용
3. 서버 영역
    - 실시간 정보 제공을 위한 Firebase 기반 데이터베이스 
        - 불법주차 차량의 사진과 영상처리 영역의 처리결과를 저장하며 사용자 디바이스 영역의 실시간 동기화를 위해 Firebase를 사용
4. 사용자 디바이스 영역
    - 어플리케이션(주차장 이용자 전용)
        - 주차장 이용자를 대상으로 주차장의 잔여 주차공간 및 이용률을 실시간으로 제공하기 위해 Android OS에 기반 됨
    - 웹 페이지(주차장 관리자 전용)
        - 주차장 관리자를 대상으로 실시간 주차 현황 및 불법주차 차량의 정보를 제공하기 위해, 웹 페이지는 HTML/JavaScript에 기반 됨


## 시스템 구조
<p align="center"><img src="./img/전체 아키텍쳐.png" width="800" style="border-radius:10%"></p>

## 개발 환경 
<table>
    <thead align="center">
        <tr align="center">
            <th>  </th>
            <th>IoT CCTV 영역</th>
            <th>영상 처리</th>
            <th>Wep App</th>
            <th>Android App</th>
        </tr>
    </thead>
    <tbody align="center">
        <tr>
            <td><b> 개발언어 </b></td>
            <td>Python</td>
            <td>Python</td>
            <td>HTML, JavaScript</td>
            <td>JAVA</td>
        </tr>
        <tr>
            <td><b> 운영체제 </b></td>
            <td>Raspbian</td>
            <td>Ubuntu 18.04</td>
            <td>Windows 10</td>
            <td>Android OS</td>
        </tr>
        <tr>
            <td><b> 프레임워크 </b></td>
            <td> </td>
            <td>Apache Spark</td>
            <td> </td>
            <td> </td>
        </tr>
        <tr>
            <td><b> 라이브러리 </b></td>
            <td></td>
            <td>OpenCV,Pyspark3.0,Tensorflow2.0,Numpy 1.16</td>
            <td>Firebase JavaScript SDK</td>
            <td>Firebase Android SDK</td>
        </tr>
        <tr>
            <td><b> 개발 보드</b></td>
            <td>RPI3B+</td>
            <td> </td>
            <td> </td>
            <td> </td>
        </tr>
        <tr>
            <td><b> 데이터베이스 </b></td>
            <td colspan=4>Firebase RealtimeDB, Google Cloud Storage</td>
        </tr>
        <tr>
            <td><b> 버전 관리 </b></td>
            <td colspan=4>GitHub</td>
        </tr>
        <tr>
            <td><b> 기타 </b></td>
            <td colspan=4>Google Meet, Google Drive</td>
        </tr>
    </tbody>
</table>


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
  - 정영석(Project Leader) / dnfkdi1995@gmail.com
  - 이연희 / yhlee98y@gmail.com
  - 노재영 / groove38@naver.com
  - 손주형 / jhson722@naver.com
  - 김도경 / jes1456@naver.com



