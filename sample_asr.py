import azure.cognitiveservices.speech as speechsdk
import time

SPEECH_API_KEY = 'c472e5d9fc734c7e95de345bf286e4c8'
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
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

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
        time.sleep(.5)
except KeyboardInterrupt:
    pass

speech_recognizer.stop_continuous_recognition()