from server.server import Server
import sys
HOST = '127.0.0.1'
PORT = 8888
src_type = 'file' # 'file' or 'webcam'

if __name__ == "__main__":
    while True:
        server = Server(HOST, PORT, src_type)
        server.run()

