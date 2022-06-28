import azure.cognitiveservices.speech as speechsdk
import time
import json
import ffmpeg
from publisher import TCPPublisher

# FFmpeg
process = (
    ffmpeg
    .input('udp://127.0.0.1:5001', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    .output('-', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    .run_async(pipe_stdout=True)
)

# パブリッシャーの設定
pub = TCPPublisher(bind_ip='127.0.0.1', port=10001)
pub.start()

SPEECH_API_KEY = 'AzureのAPIキー'
SERVICE_REGION = 'japanwest'
LANG = 'ja-JP'

done = False

# Callback funcs
def recognizing_cb(evt):
    print(f'Recognizing: {evt.result.text}')
    json_str = json.dumps(dict(topic='recognizing', result=evt.result.text))
    pub.publish(json_str)

def recognized_cb(evt):
    print(f'Recognized: {evt.result.text}')
    # Publish recognized results
    json_str = json.dumps(dict(topic='recognized', result=evt.result.text))
    pub.publish(json_str)

def session_started_cb(evt):
    print(f'Session started: {evt}')

def session_stopped_cb(evt):
    print(f'Session stopped: {evt}')
    global done
    done = True

def canceled_cb(evt):
    print(f'CLOSING on {evt}')
    global done
    done = True


# Config a speech recognizer
speech_config = speechsdk.SpeechConfig(subscription=SPEECH_API_KEY, region=SERVICE_REGION)
speech_config.speech_recognition_language=LANG

stream = speechsdk.audio.PushAudioInputStream()
audio_config = speechsdk.audio.AudioConfig(stream=stream)

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# Connect callbacks to the events fired by the speech recognizer
speech_recognizer.recognizing.connect(recognizing_cb)
speech_recognizer.recognized.connect(recognized_cb)
speech_recognizer.session_started.connect(session_started_cb)
speech_recognizer.session_stopped.connect(session_stopped_cb)
speech_recognizer.canceled.connect(canceled_cb)

# Start continuous speech recognition
speech_recognizer.start_continuous_recognition()
try:
    while not done:
        in_bytes = process.stdout.read(1024)
        if not in_bytes:
            break

        stream.write(in_bytes)
except KeyboardInterrupt:
    pass

speech_recognizer.stop_continuous_recognition()
pub.close()
