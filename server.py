import socket
# global variable setting ######
HOST, PORT = '127.0.0.1', 8888
################################
# class, function definition


class Server():
    def __init__(self):
        pass


#################################


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(10)
print("Server is listening")
while(True):
    client, address = server_socket.accept()
    # resolve RTP packet
    request_type = ''
    if request_type == 'SETUP':
        pass
    elif request_type == 'PLAY':
        pass
    elif request_type == 'PAUSE':
        pass
    elif request_type == 'TEARDOWN':
        client.close()
