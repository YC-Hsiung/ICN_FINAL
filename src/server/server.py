import socket
import threading
from utils.video_streaming import VideoStreaming
from utils.rtsp_rtp import RTPPacket, RTSPPacket
 
# global variable setting ######
RECV_BUFFER = 4096
SESSION_ID = 0

class Server():
    def __init__(self, host, port):
        self._state = 'INIT'
        print("Server state: INIT")
        self._host = host
        self._rtsp_port = port

    def run(self):
        # wait for setup
        self._rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._rtsp_socket.bind((self._host, self._rtsp_port))
        self._rtsp_socket.listen()
        print("The RTSP server is listening...")

        self._client, self._client_addr = server.accept()
        print(str(slef._client_addr)+" connected")

        while self._state != 'FINISHED':
            packet = self._get_rtsp_packet()

            if packet.request_type = RTSPPacket.SETUP: # TODO
                if self._state != "INIT":
                    raise Exception("SETUP request received while not in INIT state.")
                self._setup()

            elif packet.request_type = RTSPPacket.PLAY:
                if self._state == 'PLAYING': # already playing
                    print('Already playing')
                elif self._state == 'INIT':
                    raise Exception("PLAY request received while the server is not setup.")
                else:
                    self._state = 'PLAYING'
                    print("Server state: PLAYING")
                    self._rtp_ctrl.set()

            elif packet.request_type = RTSPPacket.PAUSE:
                if self._state == 'READY': # already paused
                    print('Already paused.')
                elif self._state == 'INIT':
                    raise Exception("PLAY request received while the server is not setup.")
                else:
                    self._state = 'READY'
                    print("Server state: READY")
                    self._rtp_ctrl.clear()

            elif packet.request_type = RTSPPacket.TEARDOWN:
                self._teardown()

            # send RTSP response
            response = RTSPPacket.build_response(packet.seq_num, SESSION_ID)
            self._client(response.encode())

    def _teardown(self):
        self._rtp_ctrl.clear()
        self._rtsp_socket.close()
        self._rtp_socket.close()
        self._video_stream.close()
        self._state = 'FINISHED'
        print("Server state: FINISHED")

    
    def _setup(self, packet):
        # setup RTP
        self._rtp_port = packet.dst_port # TODO: confirm?
        self._rtp_socket.connect((self._client_addr, self._rtp_port))
        video_path = packet.video_file_path
        print(f"Video file path: {video_path}")
        self._video_stream = VideoStreaming(video_path)
        self._rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._rtp_ctrl = threading.Event()
        self._rtp_thread = threading.Thread(target=self._send_rtp_packet, args=(self._rtp_ctrl,))
        self._rtp_thread.setDaemon(True)
        self._state = 'READY'
        print("Server state: READY")

    def _send_rtp_packet(self, event):
        while True:
            event.wait()

            frame = self._video_stream.get_next_frame()
            frame_num = self._video_stream.current_frame_number
            timestamp = frame_num // VideoStreaming.FPS * 1000

            # EOF
            if frame_num >= self._video_stream.??? : #TODO: video length?
                self._teardown()
                break

            # prepare RTP packet
            packet = RTPPacket(26, frame_num, timestamp, frame)

            # send RTP packet
            print(f"\tRTP thread: sending frame {frame_num}")
            for i in range(len(packet)):
                self._rtp_socket.send(packet[i]) # TODO: flow control?

    def _get_rtsp_packet(self):
        message = self._client.recv(RECV_BUFFER)
        packet = RTSPPacket.from_request(message)
        return packet

