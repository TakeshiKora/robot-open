import robotop as op
import time
from pydub import AudioSegment


print('現在の関節角度を取得する。')
axes = op.read_axes('10.1.1.107', 22222)
print(axes)
time.sleep(2)


print('1秒間で左手を上げる。')
servo_map = dict(L_SHOU=0)
pose = dict(Msec=1000, ServoMap=servo_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(2)


print('0.5秒間で左手を下ろし、右手を上げ、反時計回りに30度回転し、両目の色を青にする。')
servo_map = dict(L_SHOU=-90, R_SHOU=0, BODY_Y=30)
led_map = dict(R_EYE_R=0, R_EYE_G=0, R_EYE_B=255,
                L_EYE_R=0, L_EYE_G=0, L_EYE_B=255)
pose = dict(Msec=500, ServoMap=servo_map, LedMap=led_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(2)

print('ポーズをリセットする。')
servo_map = dict(HEAD_R=0, HEAD_P=-5, HEAD_Y=0, BODY_Y=0, 
                L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)
led_map = dict(L_EYE_R=255, L_EYE_G=255, L_EYE_B=255, 
                R_EYE_R=255, R_EYE_G=255, R_EYE_B=255)
pose = dict(Msec=1000, ServoMap=servo_map, LedMap=led_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(2)

print('1秒間で左手を挙げる動作を0.3秒後に止める。')
servo_map = dict(L_SHOU=0)
pose = dict(Msec=1000, ServoMap=servo_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(0.3)
op.stop_pose('10.1.1.107', 22222)
time.sleep(2)

print('モーション（ポーズのリスト）を実行する。')
nod_motion = [
    dict(Msec=250, ServoMap=dict(R_SHOU=105,HEAD_P=-15,R_ELBO=0, L_ELBO=-3, L_SHOU=-102)),
    dict(Msec=250, ServoMap=dict(R_SHOU=77, HEAD_P=20, R_ELBO=17,L_ELBO=-17,L_SHOU=-79 )),
    dict(Msec=250, ServoMap=dict(R_SHOU=92, HEAD_P=-5, R_ELBO=5, L_ELBO=-7, L_SHOU=-88 ))
]
op.play_motion('10.1.1.107', 22222, nod_motion)
time.sleep(2)

print('モーションを0.25秒後に止める。')
nod_motion = [
    dict(Msec=250, ServoMap=dict(R_SHOU=105,HEAD_P=-15,R_ELBO=0, L_ELBO=-3, L_SHOU=-102)),
    dict(Msec=250, ServoMap=dict(R_SHOU=77, HEAD_P=20, R_ELBO=17,L_ELBO=-17,L_SHOU=-79 )),
    dict(Msec=250, ServoMap=dict(R_SHOU=92, HEAD_P=-5, R_ELBO=5, L_ELBO=-7, L_SHOU=-88 ))
]
op.play_motion('10.1.1.107', 22222, nod_motion)
time.sleep(0.25)
op.stop_motion('10.1.1.107', 22222)
time.sleep(2)

print('アイドル動作を実行する（10秒間）。')
op.play_idle_motion('10.1.1.107', 22222)
time.sleep(10)

print('アイドル動作を止める。')
op.stop_idle_motion('10.1.1.107', 22222)
time.sleep(2)

print('5秒のビートジェスチャを生成し実行する。')
end_servo_map = dict(L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)
servo_map_list = [
    dict(R_SHOU=59, R_ELBO=23, L_ELBO=-21, L_SHOU=-63),
    dict(R_SHOU=32, R_ELBO=84, L_ELBO=-80, L_SHOU=-16),
    dict(R_SHOU=15, R_ELBO=84, L_ELBO=-76, L_SHOU=-40),
    dict(R_SHOU=57, R_ELBO=20, L_ELBO=-80, L_SHOU=-46),
    dict(R_SHOU=29, R_ELBO=92, L_ELBO=-36, L_SHOU=-74),
    dict(R_SHOU=75, R_ELBO=30, L_ELBO=-31, L_SHOU=-79)
]
beat_motion = op.make_beat_motion(5000, servo_map_list, end_servo_map)
op.play_motion('10.1.1.107', 22222, beat_motion)
time.sleep(5)

print('wavファイルを再生する。')
sound = AudioSegment.from_file('sample.wav', 'wav')
op.play_wav('10.1.1.107', 22222, 'sample.wav')
time.sleep(sound.duration_seconds)

print('Wavファイルの再生とビートジェスチャを組み合わせる。')
sound = AudioSegment.from_file('sample.wav', 'wav')
op.play_wav('10.1.1.107', 22222, 'sample.wav')
beat_motion = op.make_beat_motion(sound.duration_seconds * 1000, servo_map_list, end_servo_map)
op.play_motion('10.1.1.107', 22222, beat_motion)
time.sleep(sound.duration_seconds)
