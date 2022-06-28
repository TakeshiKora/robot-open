import cv2

cap = cv2.VideoCapture('udp://127.0.0.1:5000')
# カスケード分類器の選択
cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') 
try:
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is None:
            break

        # 認識
        recognized_rects = cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=2, minSize=(1, 1))
        for rect in recognized_rects:
            cv2.rectangle(frame, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (255, 255, 255), thickness=2)

        print(recognized_rects)

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt

except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
