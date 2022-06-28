import cv2

cap = cv2.VideoCapture('udp://127.0.0.1:5000')
try:
    while(cap.isOpened()):
        ret, frame = cap.read()
        if frame is not None:
            break

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            raise KeyboardInterrupt

except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
