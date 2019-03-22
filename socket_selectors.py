import socket
import selectors
import logging
import time

HOST = 'localhost'
PORT = '5000'

logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(message)s]')

class SelectorServer:

    def __init__(self, host, port):
        self.main_socket = socket.socket()
        self.main_socket.bind((host, port))
        self.main_socket.listen(100)
        self.main_socket.setblocking(False)


        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket, 
                                events=selectors.EVENT_READ, 
                                data=self.on_accept)

        self.current_peers = {}

    def on_accept(self, sock, mask):
        conn, addr = self.main_socket.accept()
        logging.info('accepted connection from {0}'.format(addr))
        conn.setblocking(False)

        self.current_peers[conn.fileno()] = conn.getpeername()

        self.selector.register(fileobj=conn, events=selectors.EVENT_READ,
                                data=self.on_read)

    def on_read(self, conn, mask):

        try:
            data = conn.recv(1024)
            if data:
                peername = conn.getpeername()
                logging.info('got data from {}: {!r}'.format(peername, data))
                conn.send(data)
            else:
                self.close_connection(conn)

        except ConnectionResetError:
                self.close_connection(conn)

    def close_connection(self, conn):
        
        peername = self.current_peers[conn.fileno()]
        logging.info('closing connection to {0}'.format(peername))
        del self.current_peers[conn.fileno()]
        self.selector.unregister(conn)
        conn.close()

    def serve_forever(self):
        last_report_time = time.time()

        while True:

            events = self.selector.select(timeout=0.2)

            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)

            cur_time = time.time()

            if cur_time - last_report_time > 1:
                logging.info('Running report...')
                logging.info('Num active peers = {0}'.format(
                                len(self.current_peers)))
                last_report_time = cur_time