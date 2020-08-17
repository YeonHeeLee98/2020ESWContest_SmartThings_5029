import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
from uuid import uuid4


#Firebase database 인증 및 앱 초기화
cred = credentials.Certificate("eswcontest-smartthings-firebase-adminsdk-sawj4-5b7fed513d.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://eswcontest-smartthings.firebaseio.com", 'storageBucket': "eswcontest-smartthings.appspot.com"
})
#버킷은 바이너리 객체의 상위 컨테이너이다. 버킷은 Storage에서 데이터를 보관하는 기본 컨테이너이다.
bucket = storage.bucket()

def fileUpload(file, car_num_name):
    blob = bucket.blob('images/'+car_num_name + '.jpg') # 사진이 저장 될 주소
    #new token and metadata 설정
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token} #access token이 필요하다.
    blob.metadata = metadata

    #upload file
    blob.upload_from_filename(filename=file, content_type='image/jpeg')
    print(blob.public_url)

def firebase_update(num,value):

    ref = db.reference().child('object/carData') #db 위치 지정
    # ref2 = db.reference().child('object/carData2')  # db 위치 지정
    num = num
    value = value
    names = ['car','carEmpty','number']

    dic={}
    for i in range(len(num)):
        dic[names[0]+str(num[i])] = { names[1] : bool(value[i]),names[2] : num[i]}

    print(dic)
    ref.update(dic) # d여기에 json 내용
    # ref2.update(dic)  # d여기에 json 내용

def fire_base_carnum(car_char):
    ref = db.reference().child('object/guestData') #db 위치 지정
    now = datetime.now()
    for car_num in car_char:
        ref.push(
            {
            "carNum":car_num,
            "date":now.strftime('%Y.%m.%d'),
            'time':now.strftime('%H:%M:%S')
            })
        # print(car_num)

def fire_base_illegal(car_count):
    ref = db.reference().child('object/cntIllegal')
    ref.update(
        {
        "value":str(car_count)
        })