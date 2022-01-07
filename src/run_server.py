from server.server import Server
import sys
HOST = '127.0.0.1'
PORT = 8888

if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.run()

