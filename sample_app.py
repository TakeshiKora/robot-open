import json
import subscriber
import queue
import threading

FACE_RECG_PORT   = 10000
SPEECH_RECG_PORT = 10001


def run(q:queue.Queue):
    while True:
        packet = q.get()
        if   packet['port'] == FACE_RECG_PORT:
            msg_obj = json.loads(packet["msg"])
            print(f'画像認識結果：{msg_obj}')
        elif packet['port'] == SPEECH_RECG_PORT:
            msg_obj = json.loads(packet["msg"])
            print(f'音声認識結果：{msg_obj}')

        if 'quit' in packet: break



if __name__ == '__main__':
    q = queue.Queue()
    # 画像認識ポートをサブスクライブ
    subscriber.TCPSubscriber('127.0.0.1', FACE_RECG_PORT, q).subscribe()
    # 音声認識ポートをサブスクライブ
    subscriber.TCPSubscriber('127.0.0.1', SPEECH_RECG_PORT, q).subscribe()
    # 受け取ったデータを処理するスレッドを実行
    threading.Thread(target=run, args=(q,), daemon=True).start()
    try:
        while True:
            input('Ctrl-cで終了\n')
    except KeyboardInterrupt:
        packet = dict(quit=True)
        q.put(json.dumps(packet))
