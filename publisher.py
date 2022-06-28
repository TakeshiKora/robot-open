import socket
import threading

class TCPPublisher(object):

    def __init__(self, bind_ip: str, port: int):
        self.__conns = {}
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.bind((bind_ip, port))
        self.__sock.listen(1)

    def start(self):
        t = threading.Thread(target=self.__run, daemon=True)
        t.start()

    def publish(self, text: str):
        disposed_conns = {}
        for addr, conn in self.__conns.items():
            try:
                ret = self.__send(conn, text.encode('utf8'))
            except ConnectionResetError:
                disposed_conns[addr] = conn

        for addr, conn in disposed_conns.items():
            conn.close()
            self.__conns.pop(addr)

    def close(self):
        for addr, conn in self.__conns.items():
            conn.close()
            print(f'{addr} is closed.')


    def __run(self):
        while True:
            print("Waiting for connection")
            conn, addr = self.__sock.accept()
            print("Connected to addr IP: {}".format(addr))
            self.__conns[addr] = conn

    def __send(self, conn:socket.socket, data=bytes):
        size = len(data)
        conn.sendall(size.to_bytes(4, byteorder='big'))
        conn.sendall(data)
