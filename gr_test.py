#ランダム・時間
import random
import time
#顔認識して動く用
import cv2
import robotop as op


#変数↓
IP = '10.1.1.107'
PORT = 22222
#顔認識した人の方向
servo_map = {}
#顔認識できているかどうか
flag = False 
#n秒ごとに呼びかけ
n = 5 

#ポーズをリセットする
def reset():
    servo_map = dict(HEAD_R=0, HEAD_P=-5, HEAD_Y=0, BODY_Y=0, 
                 L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)
    led_map = dict(L_EYE_R=255, L_EYE_G=255, L_EYE_B=255, 
               R_EYE_R=255, R_EYE_G=255, R_EYE_B=255)
    pose = dict(Msec=1000, ServoMap=servo_map, LedMap=led_map) 
    op.play_pose(IP, PORT, pose)

#顔認識した方向を向く
def look(x:int, y:int, width=320, height=240):
    """ x, y を見る """
    curr_servo_map = op.read_axes(IP, PORT)
    # 画面中央から指定位置までのYawとPitchの角度を計算
    dx = x - width / 2
    dy = y - height / 2
    dyaw = round(dx * 48 / width) * (-1) # dx : width(pixel) = dyaw : 48deg
    dpitch = round(dy * 36 / height) # dy : height(pixel) = dpitch : 36deg
    # 頭部の関節の回転角を計算
    #servo_map = {}
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
    pose = dict(Msec=500, ServoMap=servo_map)
    op.play_pose(IP, PORT, pose)



cap = cv2.VideoCapture('udp://127.0.0.1:5000')
# カスケード分類器の選択
cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
timestamp = time.time()

try:
    reset()
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
        
        #顔認識成功したら　方向を取得する
        if time.time() - timestamp > 0.5:
            print(recognized_rects)
            if len(recognized_rects) != 0:
                x1, y1, w, h = recognized_rects[0]
                x = x1 + w // 2
                y = y1 + h // 2
                print(f'x={x}, y={y}')
                look(x, y)
                timestamp = time.time()
                flag = True
        
        #顔認識成功したとき　会話
        if flag:
            #"文化情報学部に興味はある？"
            op.play_wav(IP, PORT, 'dialog0.wav')
            time.sleep(3.5)
            #ちょっとお話聞いてみてよ！
            servo_map = dict(L_SHOU=90, R_SHOU=-90)
            led_map = dict(R_EYE_R=255, R_EYE_G=255, R_EYE_B=0,
                           L_EYE_R=255, L_EYE_G=255, L_EYE_B=0)
            pose2 = dict(Msec=1000, ServoMap=servo_map, LedMap=led_map)
            op.play_pose(IP, PORT, pose2)
            op.play_wav(IP, PORT, 'dialog1.wav')
            time.sleep(4.5)
            reset()
            #文化情報学部は文理融合の学部で、
            op.play_wav(IP, PORT, 'dialog2.wav')
            time.sleep(4.5)
            #プログラミングだけじゃなくて、言語や行動などについて
            op.play_wav(IP, PORT, 'dialog3.wav')
            time.sleep(5.5)
            #君の好きな分野を学ぶことができるよ
            op.play_wav(IP, PORT, 'dialog4.wav')
            time.sleep(4.5)
            #ロボットについて学ぶこともできるんだ
            op.play_wav(IP, PORT, 'dialog5.wav')
            time.sleep(4.5)
            #入学してくれたら、僕にまた会えると思うから
            op.play_wav(IP, PORT, 'dialog6.wav')
            time.sleep(4.5)
            #受験頑張ってね！
            op.play_wav(IP, PORT, 'dialog7.wav')
            time.sleep(8)
            flag = False
            timestamp = time.time()
        
        #n秒たっても顔認識できなかった時　呼びかけ
        if time.time() - timestamp > n:
            num = random.randint(0,2)
            servo_map = dict(L_SHOU=0)
            pose2 = dict(Msec=1000, ServoMap=servo_map)
            op.play_pose(IP, PORT, pose2)
            if num == 0: #こんにちは
                op.play_wav(IP, PORT, 'kon.wav')
            elif num == 1: #ちょっとお話聞いていってよ！
                op.play_wav(IP, PORT, 'ohanashi.wav')
            else: #僕はソータだよ
                op.play_wav(IP, PORT, 'sota.wav')
            time.sleep(2)
            servo_map = dict(L_SHOU=-90)
            pose2 = dict(Msec=1000, ServoMap=servo_map)
            op.play_pose(IP, PORT, pose2)
            time.sleep(3)
            timestamp = time.time()



except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
 