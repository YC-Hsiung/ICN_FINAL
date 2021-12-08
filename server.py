import socket
# global variable setting ######
HOST, PORT = '127.0.0.1', 8888
################################
# class, function definition


class Server():
    def __init__(self, socket):
        self.state = 'INIT'
        self.socket = socket

#################################


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(10)
print("Server is listening")
while(True):
    client, address = server_socket.accept()
    print(str(address)+" connected.")
    request = str(client.recv(1024), encoding='utf-8') # may force encoding

    # resolve RTSP packet type and version
    request_lines = request.split('\r\n')
    request_type = request_lines[0].split()[0]
    rtsp_ver = request_lines[0].split()[-1]
    if not rtsp_ver == 'RTSP/1.0':
        raise ValueError("Unsupported RTSP version.")

    if request_type == 'SETUP':
        pass
    elif request_type == 'PLAY':
        pass
    elif request_type == 'PAUSE':
        pass
    elif request_type == 'TEARDOWN':
        # clean up
        client.close()
    else:
        raise Exception('Unsupported request type')
