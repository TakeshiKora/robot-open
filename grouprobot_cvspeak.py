import cv2
import robotop as op
from gtts import gTTS 
from pydub import AudioSegment


cap = cv2.VideoCapture('udp://127.0.0.1:5000')
try:
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is not None:
            break

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt
            def make_wav(text:str, output_file_path='temp.wav', slow=False) -> int:
                gTTS(text=text, lang='ja', slow=slow).save('temp.mp3')
                sound = AudioSegment.from_mp3('temp.mp3')
                sound.export(output_file_path, format='wav')
                return sound.duration_seconds

            print('発話させたい文章を入力してください。終了は ctrl + c')
            while True:
                text = input('> ')
                make_wav(text)
                op.play_wav('10.1.1.107', 22222, 'temp.wav')

except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
    
