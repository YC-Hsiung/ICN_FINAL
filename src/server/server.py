import socket
import threading
from utils.video_streaming import VideoStreaming
from utils.rtsp_rtp import RTPPacket, RTSPPacket
import time

from time import sleep

# global variable setting ######
RECV_BUFFER = 4096
SESSION_ID = 0


class Server():
    def __init__(self, host, port, stream_type='file'):
        self._state = 'INIT'
        print("Server state: INIT")
        self._host = host
        self._rtsp_port = port
        self.stream_type = stream_type
        if self.stream_type == 'file':
            self.send_period = 1000//VideoStreaming.FPS/1000.
        elif self.stream_type == 'webcam':
            self.send_period = 1.0/40
        else:
            raise Exception('Unsupported source type.')

    def run(self):
        # wait for setup
        self._rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._rtsp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self._rtsp_socket.bind((self._host, self._rtsp_port))
        self._rtsp_socket.listen()
        print("The RTSP server is listening...")

        self._client, self._client_addr = self._rtsp_socket.accept()
        print(str(self._client_addr)+" connected")

        while self._state != 'FINISHED':
            packet = self._get_rtsp_packet()

            if packet.request_type == RTSPPacket.SETUP:  # TODO
                if self._state != "INIT":
                    raise Exception(
                        "SETUP request received while not in INIT state.")
                self._setup(packet)

            elif packet.request_type == RTSPPacket.PLAY:
                if self._state == 'PLAYING':  # already playing
                    print('Already playing')
                elif self._state == 'INIT':
                    raise Exception(
                        "PLAY request received while the server is not setup.")
                else:
                    self._state = 'PLAYING'
                    print("Server state: PLAYING")
                    self._rtp_ctrl.set()

            elif packet.request_type == RTSPPacket.PAUSE:
                if self._state == 'READY':  # already paused
                    print('Already paused.')
                elif self._state == 'INIT':
                    raise Exception(
                        "PLAY request received while the server is not setup.")
                else:
                    self._state = 'READY'
                    print("Server state: READY")
                    self._rtp_ctrl.clear()

            elif packet.request_type == RTSPPacket.TEARDOWN:
                self._teardown()

            # send RTSP response
            response = RTSPPacket.build_response(packet.seq_num, SESSION_ID)
            print("sending response:", response)
            self._client.sendto(response.encode(),
                                (self._client_addr, self._rtsp_port))

    def _teardown(self):
        self._rtp_ctrl.clear()
        self._rtsp_socket.close()
        self._rtp_socket.close()
        self._video_stream.close()
        self._state = 'FINISHED'
        print("Server state: FINISHED")

    def _setup(self, packet):
        # setup RTP socket
        self._rtp_port = packet.rtp_port
        self._client_addr = self._client_addr[0]
        self._rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rtp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

        # setup video streaming
        video_path = packet.video_path
        print(f"Video file path: {video_path}")
        self._video_stream = VideoStreaming(video_path, src_type=self.stream_type)
        # setup rtp thread
        self._rtp_ctrl = threading.Event()
        self._rtp_thread = threading.Thread(
            target=self._send_rtp_packet, args=(self._rtp_ctrl,))
        self._rtp_thread.setDaemon(True)
        self._rtp_thread.start()
        self._state = 'READY'
        print("Server state: READY")

    def _send_rtp_packet(self, event):
        first_package = True
        while True:
            event.wait()
            time_start = time.process_time()
            if first_package:
                packet = RTPPacket(
                    26, self._video_stream.video_length, -1, self._video_stream.JPEG_EOF)
                first_package = False
            else:
                try:
                    frame = self._video_stream.get_next_frame()
                    frame_num = self._video_stream.current_frame_number
                    print(frame_num)
                    print(frame[:10], frame[-10:])
                    timestamp = frame_num // VideoStreaming.FPS * 1000
                    # reached end of video
                    if not frame:
                        self._teardown()
                        break
                except ValueError as e:
                    print("wrong file format")

                # prepare RTP packet
                packet = RTPPacket(26, frame_num, timestamp, frame)

                # send RTP packet
                print(f"\tRTP thread: sending frame {frame_num}")
            packet_in_bytes = packet.getpacket()

            # TODO: NEED TO BE MODIFIED
            print("sending RTP packet: ")
            while packet_in_bytes:
                try:
                    self._rtp_socket.sendto(packet_in_bytes[:RECV_BUFFER],
                                            (self._client_addr, self._rtp_port))
                    print(packet_in_bytes[:RECV_BUFFER])
                except socket.error as e:
                    print(f"failed to send rtp packet: {e}")
                    break
                # trim bytes sent
                packet_in_bytes = packet_in_bytes[RECV_BUFFER:]
            print("packet sent.")
            time_end = time.process_time()
            elapsed_time = time_end - time_start

            if elapsed_time < self.send_period:
                self._better_sleep(self.send_period-elapsed_time)

    def _get_rtsp_packet(self):
        message = self._client.recv(RECV_BUFFER)
        packet = RTSPPacket.from_request(message)
        return packet
    
    def _better_sleep(self, sec, expected_inaccuracy=0.3):
        start = time.process_time()
        end = start+sec
        if sec-expected_inaccuracy > 0:
            time.sleep(sec-expected_inaccuracy)
        while time.process_time() < end:
            continue
        return
