# -*- coding: cp932 -*-
from base64 import b64encode
import cv2
from sys import argv
import json
import requests
from pynput.mouse import Button, Listener
import pyautogui as pgui
from bluetooth import *

print("起動中")

ENDPOINT_URL = 'ENDPOINT_URL'
API_KEY = 'API_KEY'
capture = cv2.VideoCapture(0)
print("完了")

def facedetector_gcv(img, image_path, max_results, response):
    result = ''
    # base64convert用に読み込む
    image = open(image_path, 'rb').read()

    # 顔を検出するやつのResponse作成
    # 返り値用
    s = ''
    # 'faceAnnotations'があれば顔あり
    if 'faceAnnotations' in response.json()['responses'][0]:
        print('test')
        faces = response.json()['responses'][0]['faceAnnotations']

        # 画像情報
        s += image_path + ' '
        s+= response.text
        # OpenCVで矩形を書き込み
        for face in faces:

            #笑顔ならば左矢印入力
            if face['joyLikelihood'] == 'VERY_LIKELY' or face['joyLikelihood'] == 'LIKELY':
                result = 'true'
            else:
                result = 'false'
                
                
            # 0と2が両端の番地
#            x = face['fdBoundingPoly']['vertices'][0]['x']
#            y = face['fdBoundingPoly']['vertices'][0]['y']
#            x2 = face['fdBoundingPoly']['vertices'][2]['x']
#            y2 = face['fdBoundingPoly']['vertices'][2]['y']
#            cv2.rectangle(img, (x, y), (x2, y2), (0, 0, 255), thickness=10)
            # 矩形情報を保存

    # 矩形が書き込まれた画像とs = 'file_name x1 y1 x2 y2'
    # 顔が無ければsは空
    return img, s, result

def image_capture():
    while True:
        ret, image = capture.read()

        if ret == False:
            continue
        
        cv2.imwrite("image.jpg", image)
        break

    cv2.destroyAllWindows()
    
    image = open('image.jpg', 'rb').read()

    img_requests = []
    ctxt = b64encode(image).decode()
    img_requests.append({
            'image': {'content': ctxt},
            'features': [{
                'type': 'FACE_DETECTION',
                'maxResults': 5
            }]
    })

    response = requests.post(ENDPOINT_URL,
                             data=json.dumps({"requests": img_requests}).encode(),
                             params={'key': API_KEY},
                             headers={'Content-Type': 'application/json'})

    #   for idx, resp in enumerate(response.json()['responses']):
    #      print(json.dumps(resp, indent=2))
    #if 'faceAnnotations' in response.json()['responses'][0]:
    # 画像読み込み

    image_path = 'image.jpg'
#    max_results = 8
#    img = cv2.imread(sample_img_path)


    # Google API
#    img, s, result = facedetector_gcv(img, sample_img_path, max_results, response)

    # 画像出力
#    cv2.imwrite('output_' + sample_img_path, img)


    result = 'false'
    s = ''
    if 'faceAnnotations' in response.json()['responses'][0]:
        print('detected')
        faces = response.json()['responses'][0]['faceAnnotations']

        # 画像情報
        s += image_path + ' '
        s+= response.text
        # OpenCVで矩形を書き込み
        for face in faces:

            #笑顔ならば左矢印入力
            if face['joyLikelihood'] == 'VERY_LIKELY' or face['joyLikelihood'] == 'LIKELY':
                result = 'true'
            else:
                result = 'false'

            
        # 矩形情報出力
        f = open('./rect2.txt', 'w')
        f.write(s)
        f.close()
    else:
        print("could't detect")

    return result

def on_move(x,y):
    return
def on_scroll(x,y, dx,dy):
    return

def on_click(x, y, button, pressed):
    if pressed:
        print(button)
        if button == Button.middle:
            image_capture()

if __name__ == '__main__':
    print ('マウス入力[m] or スマホBluetooth[other word]')
    input_word = input()
    if(input_word != 'm'):    
        server_sock=BluetoothSocket( RFCOMM )
        server_sock.bind(("",PORT_ANY))
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        uuid = "UUID"

        advertise_service( server_sock, "btspp://localhost:",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ])

        print("Waiting for connection on RFCOMM channel %d" % port)

        client_sock, client_info = server_sock.accept()

        print("Accepted connection from ", client_info)

        try:
            while True:
                data = client_sock.recv(1024)
                print(data.decode('UTF-8'))
                if(data.decode('UTF-8') == 'MID'):
                    result = image_capture()
                    if(result == 'true'):
                        pgui.click(button = 'left')
                    client_sock.send(result)
                    print('complete smile:'+result)
                elif(data.decode('UTF-8') == 'LEFT'):
                    pgui.click(button = 'left')
                    client_sock.send('true')
                else:
                    client_sock.send('false')
        # raise an exception if there was any error
        except IOError:
            print(IOError)
            pass

        print("disconnected")

        client_sock.close()
        server_sock.close()
    else:
        print("マウスモードにしました。ホイールボタンクリックで識別します")
        with Listener(on_move=on_move,on_click=on_click,on_scroll=on_scroll) as listener:
            listener.join()
