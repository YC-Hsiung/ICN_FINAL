import socket
from threading import Thread
from time import sleep
from PIL import Image
from io import BytesIO

from utils.rtsp_rtp import RTSPPacket, RTPPacket
from utils.video_streaming import VideoStreaming


class Client:
    DEFAULT_CHUNK_SIZE = 4096

    DEFAULT_LOCAL_HOST = '127.0.0.1'

    def __init__(
            self,
            file_path: str,
            remote_host_address: str,
            remote_host_port: int,
            rtp_port: int):

        self._rtsp_connection = None
        self._rtp_socket = None
        self._rtp_receive_thread = None
        self._frame_buffer = []
        self._current_sequence_number = 0
        self.session_id = ''

        self.current_frame_number = -1
        self.total_frame_number = 0

        self.is_rtsp_connected = False
        self.is_receiving_rtp = False

        self.file_path = file_path
        self.remote_host_addr = remote_host_address
        self.remote_host_port = remote_host_port
        self.rtp_port = rtp_port

    def get_next_frame(self):
        if self._frame_buffer != []:
            self.current_frame_number += 1
            return self._frame_buffer.pop(0), self.current_frame_number
        return None

    @staticmethod
    def _get_frame_from_packet(packet):
        # the payload is already the jpeg
        raw = packet.payload
        frame = Image.open(BytesIO(raw))
        return frame

    def _recv_rtp_packet(self, size=DEFAULT_CHUNK_SIZE):
        recv = bytes()
        while True:
            try:
                recv += self._rtp_socket.recv(size)
                if recv.endswith(VideoStreaming.JPEG_EOF):
                    break
            except socket.timeout:
                continue
        # print(f"Received from server: {repr(recv)}")
        return RTPPacket.frompacket(recv)

    def _start_rtp_receive_thread(self):
        # setup RTP socket before sending SETUP request
        self._rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._rtp_socket.bind((self.DEFAULT_LOCAL_HOST, self.rtp_port))
        #  self._rtp_socket.settimeout(self.RTP_SOFT_TIMEOUT / 1000.)
        print("RTP port:", self.rtp_port)

        # start RTP thread
        self._rtp_receive_thread = Thread(target=self._handle_video_receive)
        self._rtp_receive_thread.setDaemon(True)
        self._rtp_receive_thread.start()

    def _handle_video_receive(self):
        first_package = True
        while True:
            if not self.is_receiving_rtp:
                sleep(5 / 1000.)  # diminish cpu hogging RTP_SOFT_TIMEOUT = 5
                continue
            packet = self._recv_rtp_packet()
            if first_package:
                if packet.payload == VideoStreaming.JPEG_EOF:
                    self.total_frame_number = packet.seq_num
                    first_package = False
                    continue
                else:
                    raise IOError

            frame = self._get_frame_from_packet(packet)
            self._frame_buffer.append(frame)

    def establish_rtsp_connection(self):
        # if self.is_rtsp_connected:
        #     print('RTSP is already connected.')
        #     return
        print(
            f"Connecting to {self.remote_host_addr}:{self.remote_host_port}...")
        self._rtsp_connection = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self._rtsp_connection.connect(
            (self.remote_host_addr, self.remote_host_port))
        self._rtsp_connection.settimeout(
            100 / 1000.)  # RSTP_SOFT_TIMEOUT = 100
        self.is_rtsp_connected = True

    def close_rtsp_connection(self):
        self._rtsp_connection.close()
        self.is_rtsp_connected = False

    def _send_request(self, request_type=RTSPPacket.INVALID):
        # if not self.is_rtsp_connected:
        #     raise Exception('rtsp connection not established. run `setup_rtsp_connection()`')
        request = RTSPPacket(
            request_type,
            self.file_path,
            self._current_sequence_number,
            self.rtp_port,
            self.session_id
        ).to_request()
        self._rtsp_connection.send(request)
        self._current_sequence_number += 1
        return self._get_response()

    def send_setup_request(self):
        self._start_rtp_receive_thread()
        response = self._send_request(RTSPPacket.SETUP)
        self.session_id = response.session_id
        return response

    def send_play_request(self):
        response = self._send_request(RTSPPacket.PLAY)
        self.is_receiving_rtp = True
        return response

    def send_pause_request(self):
        response = self._send_request(RTSPPacket.PAUSE)
        self.is_receiving_rtp = False
        return response

    def send_teardown_request(self):
        response = self._send_request(RTSPPacket.TEARDOWN)
        self.is_receiving_rtp = False
        self.is_rtsp_connected = False
        return response

    def _get_response(self, size=DEFAULT_CHUNK_SIZE):
        rcv = None
        while True:
            try:
                rcv = self._rtsp_connection.recv(size)
                break
            except socket.timeout:
                continue
        # print(f"Received from server: {repr(rcv)}")
        response = RTSPPacket.from_response(rcv)
        return response
