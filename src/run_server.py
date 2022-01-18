from server.server import Server
import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0].split('/')[-1]} <server address> <server port> <source type>")
        exit(-1)

    server_address, server_port, src_type = *sys.argv[1:],

    try:
        server_port = int(server_port)
    except ValueError:
        raise ValueError('port values should be integer')
    if src_type not in ['file', 'webcam']:
        raise ValueError("source type can only be 'webcam' or 'file'")
     
    while True:
        server = Server(server_address, server_port, src_type)
        server.run()

