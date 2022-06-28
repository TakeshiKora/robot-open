import cv2
import time
from publisher import TCPPublisher
import json


# パブリッシャーの設定
pub = TCPPublisher(bind_ip='127.0.0.1', port=10000)
pub.start()

cap = cv2.VideoCapture('udp://127.0.0.1:5000')
# カスケード分類器の選択
cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
timestamp = time.time()
try:
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            break

        recognized_rects = cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=2, minSize=(1, 1))
        for rect in recognized_rects:
            cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (255, 255, 255), thickness=2)

        if not isinstance(recognized_rects, tuple):
            print(recognized_rects)
            pub.publish(json.dumps(recognized_rects.tolist()))

        cv2.imshow('image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt

except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
    pub.close()
