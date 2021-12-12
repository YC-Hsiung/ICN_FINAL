import socket
# global variable setting ######
HOST, PORT = '127.0.0.1', 8888
DEBUG = True
RTP_HOST, RTP_PORT = '127.0.0.1', 7777  # TODO: temporary
################################
# class, function definition

# print() for debugging
def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

class Client():
    def __init__(self, host, port):
        self.filename = ''
        self.seq_num = 0
        self.id = 0
        self.port = port
        self.state = 'INIT'
        self.rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtsp_socket.connect((host, port))

    def send_request(self, request_type):
        dprint('Client: sending request', request_type)
        header = request_type+' '+self.filename+'RTSP/1.0'+'\r\n'
        header += 'CSeq: '+str(self.seq_num)+'\r\n'
        if request_type == "SETUP":
            header += "Transport: RTP/UDP; client_port= " + str(self.port) + '\r\n'

        else:
            header += "Session: " + self.id + '\r\n'

        message = header # TODO: add payload
        self.rtsp_socket.send(header.encode('utf-8'))

        # TODO: wait for response

    def setup(self):
        if self.state != 'INIT':
            return
        self.seq_num = 1
        self.send_request('SETUP')
        self.rtp_socket.bind((RTP_HOST, RTP_PORT))
        dprint('Client: connected to RTP client.')
        server_respond = 200 # TODO: parse response
        if server_respond == 200:
            self.state = 'READY'

    def play(self):
        if self.state == 'READY':
            self.seq_num += 1
            self.send_request('PLAY')
            server_respond = 200
            if server_respond == 200:
                self.state = 'PLAYING'
                # start timer

    def pause(self):
        if self.state == 'PLAYING':
            self.seq_num += 1
            self.send_request('PAUSE')
            server_respond = 200
            if server_respond == 200:
                self.state = 'PAUSE'
                # stop timer

    def teardown(self):
        self.seq_num += 1
        self.send_request('TEARDOWN')
        server_respond = 200
        if server_respond == 200:
            self.state = 'INIT'
            # stop timer


#########################################

if __name__ == "__main__":
    client = Client(HOST, PORT)
    Filename = 'sample.mp4'
    request_type = 'SETUP'
    if request_type == 'SETUP':
        client.setup()
    elif request_type == 'PLAY':
        client.play()
    elif request_type == 'PAUSE':
        client.pause()
    elif request_type == 'TEARDOWN':
        client.teardown()
