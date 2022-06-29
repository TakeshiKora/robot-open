from tkinter import Text
import cv2
import robotop as op
import time
import robotop as op
from gtts import gTTS 
from pydub import AudioSegment



IP = '192.168.11.22'
PORT = 22222

axes = op.read_axes('10.1.1.107', 22222)
print(axes)
time.sleep(2)

servo_map = dict(L_SHOU=0)
pose = dict(Msec=1000, ServoMap=servo_map)
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

servo_map = dict(HEAD_R=0, HEAD_P=-5, HEAD_Y=0, BODY_Y=0, 
                L_SHOU=-90, L_ELBO=0, R_SHOU=90, R_ELBO=0)
led_map = dict(L_EYE_R=255, L_EYE_G=255, L_EYE_B=255, 
                R_EYE_R=255, R_EYE_G=255, R_EYE_B=255)
pose = dict(Msec=1000, ServoMap=servo_map, LedMap=led_map)
op.play_pose('10.1.1.107', 22222, pose)
time.sleep(2)