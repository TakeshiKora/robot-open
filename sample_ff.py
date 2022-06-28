import ffmpeg
import azure.cognitiveservices.speech as speechsdk

# FFmpeg
process = (
    ffmpeg
    .input('udp://127.0.0.1:5001', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    .output('-', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
    .run_async(pipe_stdout=True)
)

# Azure Speech SDK
SPEECH_API_KEY = '5576f3dedf5c41d49cb652950f30394b'
SERVICE_REGION = 'japanwest'
LANG = 'ja-JP'

done = False

# Callback funcs
def recognizing_cb(evt):
    print(f'Recognizing: {evt.result.text}')

def recognized_cb(evt):
    print(f'Recognized: {evt.result.text}')

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

stream.close()
speech_recognizer.stop_continuous_recognition()
