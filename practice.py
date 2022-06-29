from tkinter import Text
import cv2
import robotop as op
import time
import robotop as op
from gtts import gTTS 
from pydub import AudioSegment



axes = op.read_axes('10.1.1.107', 22222)
print(axes)
time.sleep(2)

servo_map = dict(L_SHOU=0)
pose = dict(Msec=1000, ServoMap=servo_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(2)

servo_map = dict(HEAD_R=0, HEAD_P=-5, HEAD_Y=0, BODY_Y=0, 
                L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)
led_map = dict(L_EYE_R=255, L_EYE_G=255, L_EYE_B=255, 
                R_EYE_R=255, R_EYE_G=255, R_EYE_B=255)
pose = dict(Msec=1000, ServoMap=servo_map, LedMap=led_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(2)

def make_wav(text:str, output_file_path='temp.wav', slow=False) -> int:
    gTTS(text=text, lang='ja', slow=slow).save('temp.mp3')
    sound = AudioSegment.from_mp3('temp.mp3')
    sound.export(output_file_path, format='wav')
    return sound.duration_seconds
text = 'こんにちは。僕は文化情報学部のソータです'
make_wav(text)
op.play_wav('10.1.1.107', 22222, 'temp.wav')

IP = '10.1.1.107'
PORT = 22222

def look(x:int, y:int, width=320, height=240):
    """ x, y を見る """
    curr_servo_map = op.read_axes(IP, PORT)
    # 画面中央から指定位置までのYawとPitchの角度を計算
    dx = x - width / 2
    dy = y - height / 2
    dyaw = round(dx * 48 / width) * (-1) # dx : width(pixel) = dyaw : 48deg
    dpitch = round(dy * 36 / height) # dy : height(pixel) = dpitch : 36deg
    # 頭部の関節の回転角を計算
    servo_map = {}
    ## head yaw
    if   curr_servo_map['HEAD_Y'] + dyaw > 85:
        servo_map.update(HEAD_Y=85)
    elif curr_servo_map['HEAD_Y'] + dyaw < -85:
        servo_map.update(HEAD_Y=-85)
    else:
        servo_map.update(HEAD_Y=curr_servo_map['HEAD_Y'] + dyaw)
    ## head pitch
    if   curr_servo_map['HEAD_P'] + dpitch > 5:
        servo_map.update(HEAD_P=5)
    elif curr_servo_map['HEAD_P'] + dpitch < -27:
        servo_map.update(HEAD_P=-27)
    else:
        servo_map.update(HEAD_P=curr_servo_map['HEAD_P'] + dpitch)
    # ポーズの実行
    pose = dict(Msec=500, ServoMap=servo_map)
    op.play_pose(IP, PORT, pose)


cap = cv2.VideoCapture('udp://127.0.0.1:5000')
# カスケード分類器の選択
cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
timestamp = time.time()
try:
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            break

        # 認識
        recognized_rects = cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=2, minSize=(1, 1))
        for rect in recognized_rects:
            cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (255, 255, 255), thickness=2)

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt

        if time.time() - timestamp > 0.5:
            print(recognized_rects)
            if len(recognized_rects) != 0:
                x1, y1, w, h = recognized_rects[0]
                x = x1 + w // 2
                y = y1 + h // 2
                print(f'x={x}, y={y}')
                look(x, y)
                timestamp = time.time()


except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
