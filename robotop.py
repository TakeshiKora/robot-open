import json
import robotio as io 
import random
from typing import List

 
def read_axes(ip:str, port:int) -> dict:
    data = io.recv(ip, port, 'read_axes')
    axes = json.loads(data)
    return axes
    
def play_pose(ip:str, port:int, pose:dict):
    data = json.dumps(pose).encode('utf-8')
    io.send(ip, port, 'play_pose', data)
   
def stop_pose(ip:str, port:int):
    io.send(ip, port, 'stop_pose')
 
def play_motion(ip:str, port:int, motion:List[dict]):
    data = json.dumps(motion).encode('utf-8')
    io.send(ip, port, 'play_motion', data)
  
def stop_motion(ip:str, port:int):
    io.send(ip, port, 'stop_motion')
 
def play_idle_motion(ip:str, port:int, speed=1.0, pause=1000):
    data = json.dumps(dict(Speed=speed, Pause=pause)).encode('utf-8')
    io.send(ip, port, 'play_idle_motion', data)

def stop_idle_motion(ip:str, port:int):
    io.send(ip, port, 'stop_idle_motion')

def play_wav(ip:str, port:int, wav_file:str):
    with open(wav_file, 'rb') as f:
        data = f.read()
        io.send(ip, port, 'play_wav', data)

def stop_wav(ip:str, port:int):
    io.send(ip, port, 'stop_wav') 

def make_beat_motion(duration:int, servo_map_list:List[dict], end_servo_map:dict, speed=1.0):
    def __choose(prev, maps):
        while True:
            map = random.choice(maps)
            if map != prev:
                return map

    msec = int(1000 / speed)
    size = int(duration / msec)
    motion = []
    prev = {}
    for i in range(size):
        servo_map = __choose(prev, servo_map_list)
        motion.append(dict(Msec=msec, ServoMap=servo_map))
        prev = servo_map

    motion.append(dict(Msec=1000, ServoMap=end_servo_map))
    return motion
