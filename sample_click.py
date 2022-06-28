import cv2
import robotop as op


IP = '192.168.11.22'
PORT = 22222
WIDTH = 320
HEIGHT = 240

#----------
# OpenCV
#----------
def on_clicked(event, x, y, flags, param):
    """ 画面クリック時のコールバック関数 """
    if event == cv2.EVENT_LBUTTONUP:
        # クリック時は頭部動作、Ctrl+クリック時は頭部＋身体動作
        servo_map = calc_servo_map_head_body(x, y) if flags & cv2.EVENT_FLAG_CTRLKEY else calc_servo_map_head(x, y)
        pose = dict(Msec=500, ServoMap=servo_map)
        op.play_pose(IP, PORT, pose)
        print(pose)

def calc_dyaw_dpitch(x, y):
    """ 画面中央からクリック位置までのYawとPitchの角度を計算 """
    dx = x - WIDTH / 2
    dy = y - HEIGHT / 2
    dyaw = round(dx * 48 / WIDTH) * (-1) # dx : width(pixel) = dyaw : 48deg
    dpitch = round(dy * 36 / HEIGHT) # dy : height(pixel) = dpitch : 36deg
    return (dyaw, dpitch)

def calc_servo_map_head(x, y):
    """ 頭部の関節の回転角を計算 """
    dyaw, dpitch = calc_dyaw_dpitch(x, y)
    cur_servo_map = op.read_axes(IP, PORT)
    servo_map = {}
    # head yaw
    if   cur_servo_map['HEAD_Y'] + dyaw > 85:
        servo_map.update(HEAD_Y=85)
    elif cur_servo_map['HEAD_Y'] + dyaw < -85:
        servo_map.update(HEAD_Y=-85)
    else:
        servo_map.update(HEAD_Y=cur_servo_map['HEAD_Y'] + dyaw)
    # head pitch
    if   cur_servo_map['HEAD_P'] + dpitch > 5:
        servo_map.update(HEAD_P=5)
    elif cur_servo_map['HEAD_P'] + dpitch < -27:
        servo_map.update(HEAD_P=-27)
    else:
        servo_map.update(HEAD_P=cur_servo_map['HEAD_P'] + dpitch)
    return servo_map

def calc_servo_map_head_body(x, y):
    """ 身体を動かす場合の頭部と身体の関節の回転角の計算 """
    dyaw, dpitch = calc_dyaw_dpitch(x, y)
    cur_servo_map = op.read_axes(IP, PORT)
    servo_map = {}
    # head and body yaw
    if   cur_servo_map['BODY_Y'] + cur_servo_map['HEAD_Y'] + dyaw > 61:
        servo_map.update(BODY_Y=61, HEAD_Y=cur_servo_map['BODY_Y'] + cur_servo_map['HEAD_Y'] + dyaw - 61)
    elif cur_servo_map['BODY_Y'] + cur_servo_map['HEAD_Y'] + dyaw < -61:
        servo_map.update(BODY_Y=-61, HEAD_Y=cur_servo_map['BODY_Y'] + cur_servo_map['HEAD_Y'] + dyaw + 61)
    else:
        servo_map.update(BODY_Y=cur_servo_map['BODY_Y'] + cur_servo_map['HEAD_Y'] + dyaw, HEAD_Y=0)
    # head pitch
    if   cur_servo_map['HEAD_P'] + dpitch > 5:
        servo_map.update(HEAD_P=5)
    elif cur_servo_map['HEAD_P'] + dpitch < -27:
        servo_map.update(HEAD_P=-27)
    else:
        servo_map.update(HEAD_P=cur_servo_map['HEAD_P'] + dpitch)
    return servo_map

def calc_servo_map_pointing():
    """ ポインティングする場合の頭部と身体の関節の回転角の計算 """
    cur_servo_map = op.read_axes(IP, PORT)
    direction = 'right' if cur_servo_map['BODY_Y'] < 0 else 'left'
    if direction == 'right':
        body_y = cur_servo_map['BODY_Y'] + 20
        r_shou = 3 * cur_servo_map['HEAD_P'] + 30
        print('body_y =', body_y, 'head_p =', cur_servo_map['HEAD_P'], ' r_shou =', r_shou)
        servo_map = dict(BODY_Y=body_y, HEAD_Y=-20, R_SHOU=r_shou, R_ELBO=0)
    elif direction == 'left':
        body_y = cur_servo_map['BODY_Y'] - 20
        l_shou = -3 * cur_servo_map['HEAD_P'] - 30
        print('body_y =', body_y, 'head_p =', cur_servo_map['HEAD_P'], ' l_shou =', l_shou)
        servo_map = dict(BODY_Y=body_y, HEAD_Y=20, L_SHOU=l_shou, L_ELBO=0)
    return servo_map


cap = cv2.VideoCapture('udp://127.0.0.1:5000')
cv2.namedWindow('image')
cv2.setMouseCallback('image', on_clicked)

# Event loop
while True:
    if cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            print('Video frame is None. exit')
            break
        cv2.imshow('image',frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('p'):
            # send right-hand pointing
            servo_map = calc_servo_map_pointing()
            pose = dict(Msec=500, ServoMap=servo_map)
            op.play_pose(IP, PORT, pose)
            pass
        elif k == ord(' '):
            # send left-hand pointing
            servo_map = dict(L_SHOU=-90, R_SHOU=90)
            pose = dict(Msec=500, ServoMap=servo_map)
            op.play_pose(IP, PORT, pose)
            pass

cap.release()
cv2.destroyAllWindows()