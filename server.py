import socket
# global variable setting ######
HOST, PORT = '127.0.0.1', 8888
RTP_HOST, RTP_PORT = '127.0.0.1', 7777  # TODO: temporary

DEBUG = True
################################
# class, function definition

# print() for debugging
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

class Server():
    def __init__(self, host, port):
        self.state = 'INIT'
        self.rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtsp_socket.bind((host, port))

    def listen(self):
        self.rtsp_socket.listen(10)
        dprint("Server is listening")
        while(True):
            client, address = self.rtsp_socket.accept()
            dprint(str(address)+" connected.")
            request = str(client.recv(1024), encoding='utf-8') # may force encoding

            # resolve RTSP packet type and version
            request_lines = request.split('\r\n')
            request_type = request_lines[0].split()[0]
            rtsp_ver = request_lines[0].split()[-1]
            if not rtsp_ver == 'RTSP/1.0':
                raise ValueError("Unsupported RTSP version.")

            if request_type == 'SETUP':
                dprint('Request of type SETUP is received.')
                self.rtp_socket.connect((RTP_HOST, RTP_PORT))

                dprint('Server: connected to RTP server')

                # TODO: parse RTSP packet, response
                self.state = 'READY'

            elif request_type == 'PLAY':
                dprint('Request of type PLAY is received.')

            elif request_type == 'PAUSE':
                dprint('Request of type PAUSE is received.')

            elif request_type == 'TEARDOWN':
                dprint('Request of type SETUP is received.')
                client.close()

            else:
                raise Exception('Unsupported request type')

#################################

if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.listen()
