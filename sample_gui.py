import robotop as op
import PySimpleGUI as sg
from gtts import gTTS 
from pydub import AudioSegment

IP = '10.1.1.107'
PORT = 22222

# リセットポーズ用の定数（Sotaの場合）
home_servo_map = dict(HEAD_R=0, HEAD_P=-5, HEAD_Y=0, BODY_Y=0, 
                    L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)

# リセットポーズ用の定数（パペットの場合）
# home_servo_map = dict(HEAD_R=0, HEAD_P=0, BODY_Y=0, L_ELBO=0, R_ELBO=0)

# ビートジェスチャ用の定数（Sotaの場合）
end_beat_servo_map = dict(L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)
beat_servo_map_list = [
    dict(R_SHOU=59, R_ELBO=23, L_ELBO=-21, L_SHOU=-63),
    dict(R_SHOU=32, R_ELBO=84, L_ELBO=-80, L_SHOU=-16),
    dict(R_SHOU=15, R_ELBO=84, L_ELBO=-76, L_SHOU=-40),
    dict(R_SHOU=57, R_ELBO=20, L_ELBO=-80, L_SHOU=-46),
    dict(R_SHOU=29, R_ELBO=92, L_ELBO=-36, L_SHOU=-74),
    dict(R_SHOU=75, R_ELBO=30, L_ELBO=-31, L_SHOU=-79)
]

# ビートジェスチャ用の定数（パペットの場合）
# end_beat_servo_map = dict(HEAD_R=0, HEAD_P=0, BODY_Y=0, L_ELBO=0, R_ELBO=0)
# beat_servo_map_list = [
#     dict(HEAD_R=-14, BODY_Y=-1, HEAD_P=-1,  R_ELBO=0,   L_ELBO=-59),
#     dict(HEAD_R=22,  BODY_Y=-1, HEAD_P=-1,  R_ELBO=54,  L_ELBO=21),
#     dict(HEAD_R=-1,  BODY_Y=0,  HEAD_P=20,  R_ELBO=54,  L_ELBO=-43),
#     dict(HEAD_R=-1,  BODY_Y=-1, HEAD_P=-7,  R_ELBO=-35, L_ELBO=39),
#     dict(HEAD_R=-22, BODY_Y=-1, HEAD_P=-20, R_ELBO=10,  L_ELBO=4),
#     dict(HEAD_R=6,   BODY_Y=0,  HEAD_P=-20, R_ELBO=-24, L_ELBO=43),
#     dict(HEAD_R=6,   BODY_Y=-1, HEAD_P=-1,  R_ELBO=40,  L_ELBO=-25),
#     dict(HEAD_R=6,   BODY_Y=3,  HEAD_P=-1,  R_ELBO=-2,  L_ELBO=1)
# ]


# TTS用の便利関数
def make_wav(text:str, output_file_path='temp.wav', slow=False) -> int:
    gTTS(text=text, lang='ja', slow=slow).save('temp.mp3')
    sound = AudioSegment.from_mp3('temp.mp3')
    sound.export(output_file_path, format='wav')
    return sound.duration_seconds

def say_text(ip:str, port:int, text:str) -> int:
    duration = make_wav(text)
    op.play_wav(ip, port, 'temp.wav')
    return duration

# GUI設定
sg.theme('Black')
TEXT_DATA = [
    'こんにちは。ぼくはソータです。',
    '同志社大学文化情報学部へようこそ。',
    'これからどうぞ、よろしくお願いします。'
]
# Window layout
layout = []

# Motion buttons
idle_motion_start_btn = sg.Button('アイドルモーション開始', key='idle')
motion_stop_btn = sg.Button('アイドルモーション停止', key='stop')
reset_pose_btn = sg.Button('ポーズリセット', key='reset')
layout.append([idle_motion_start_btn, motion_stop_btn, reset_pose_btn])

# Speech buttons
for text in TEXT_DATA:
    label = sg.Text(text, size=(50, 1))
    btn = sg.Button('発話', key=f'speak_{text}')
    layout.append([label, btn])

# Text field
free_speech_field = sg.InputText(key='free_speech_field', size=(50, 1))
free_speech_btn = sg.Button('発話', key=f'free_speech')
layout.append([free_speech_field, free_speech_btn])


window = sg.Window('Sota controller', layout)

# Event loop
while True:
    event, values = window.read(timeout=1)
    if event is None:
        print('Window event is None. exit')
        break
    elif event.startswith('speak'):
        _, t = event.split('_')
        print(t)
        d = say_text(IP, PORT, t)
        beat_motion = op.make_beat_motion(d * 1000, beat_servo_map_list, end_beat_servo_map)
        print(beat_motion)
        op.play_motion(IP, PORT, beat_motion)
    elif event == 'free_speech':
        d = say_text(IP, PORT, values['free_speech_field'])
        beat_motion = op.make_beat_motion(d * 1000, beat_servo_map_list, end_beat_servo_map)
        op.play_motion(IP, PORT, beat_motion)
    elif event == 'idle':
        op.play_idle_motion(IP, PORT)
    elif event == 'stop':
        op.stop_idle_motion(IP, PORT)
    elif event == 'reset':
        servo_map = home_servo_map
        pose = dict(Msec=500, ServoMap=servo_map)
        op.play_pose(IP, PORT, pose)
    else:
        pass

window.close()