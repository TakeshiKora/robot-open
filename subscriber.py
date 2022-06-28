import socket
import threading
import queue

class TCPSubscriber(object):

    def __init__(self, ip:str, port:int, q:queue.Queue):
        self.__ip = ip
        self.__port = port
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__conn.connect((ip, port))
        self.__q = q

    def subscribe(self):
        t = threading.Thread(target=self.__run, daemon=True)
        t.start()

    def close(self):
        self.__conn.close()

    def __run(self):
        try:                
            while True:
                data = self.__recv()
                if data == b'': break
                text = data.decode('utf8')
                packet = dict(ip=self.__ip, port=self.__port, msg=text)
                self.__q.put(packet)
        except ConnectionResetError:
            pass
        self.__conn.close()

    def __read_size(self) -> int:
        b_size = self.__conn.recv(4)
        return int.from_bytes(b_size, byteorder='big')

    def __read_data(self, size:int) -> bytes:
        chunks = []
        bytes_recved = 0
        while bytes_recved < size:
            chunk = self.__conn.recv(size - bytes_recved)
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recved += len(chunk)
        return b''.join(chunks)

    def __recv(self) -> bytes:
        size = self.__read_size()
        data = self.__read_data(size)
        return data
