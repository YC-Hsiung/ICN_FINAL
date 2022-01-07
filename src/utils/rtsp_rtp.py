# %%
import re
from enum import Enum


class RTPPacket:
    HEADER_SIZE = 12
    VERSION = 0b10
    PADDING = 0b0
    EXTENSION = 0b0
    CC = 0x0
    MARKER = 0b0
    SSRC = 0x0

    def __init__(self, payload_type, seq_num, timestamp, payload):
        self.payload_type = payload_type
        self.payload = payload
        self.seq_num = seq_num
        self.timestamp = timestamp
        self.header = bytes([self.VERSION << 6 | (
            self.PADDING << 5) | (self.EXTENSION << 4) | self.CC])
        self.header += bytes([(self.MARKER << 7) | self.payload_type])
        self.header += bytes([self.seq_num >> 8])
        self.header += bytes([self.seq_num & 0xFF])
        for s in [24, 16, 8, 0]:
            self.header += bytes([(self.timestamp >> s) & 0xFF])
        for s in [24, 16, 8, 0]:
            self.header += bytes([(self.SSRC >> s) & 0xFF])

    @classmethod
    def frompacket(cls, packet):
        if len(packet) < cls.HEADER_SIZE:
            return
        header = packet[:cls.HEADER_SIZE]
        payload = packet[cls.HEADER_SIZE:]
        payload_type = header[1] & 0x7F
        seq_num = header[2] << 8 | header[3]
        timestamp = 0
        for i, b in enumerate(header[4:8]):
            timestamp = timestamp | b << (3 - i) * 8
        return cls(payload_type, seq_num, timestamp, payload)

    def getpacket(self):
        return bytes((*self.header, *self.payload))


class RTSP_Request_Type(Enum):
    INVALID = -1
    SETUP = 0
    PLAY = 1
    PAUSE = 2
    TEARDOWN = 3
    RESPONSE = 4


class RTSPPacket:
    RTSP_VERSION = 'RTSP/1.0'

    def __init__(self, resquest_type, video_path, seq_num, dst_port, session_id):
        self.request_type = resquest_type.name
        self.video_path = video_path
        self.seq_num = seq_num
        self.dst_port = dst_port
        self.session_id = session_id
        self.dst_port = dst_port

    @classmethod
    def from_response(cls, response):
        match = re.match(
            r"(?P<rtsp_version>RTSP/\d+.\d+) 200 OK\r?\n"
            r"CSeq: (?P<seq_num>\d+)\r?\n"
            r"Session: (?P<session_id>\d+)\r?\n",
            response.decode()
        )
        if match is None:
            return
        dic = match.groupdict()
        seq_num = dic.get('seq_num')
        session_id = dic.get('session_id')
        return cls(
            request_type=RTSPPacket.RESPONSE,
            seq_num=seq_num,
            session_id=session_id
        )

    @classmethod
    def build_response(cls, seq_num, session_id):
        response = '\r\n'.join((
            f"{cls.RTSP_VERSION} 200 OK",
            f"CSeq: {seq_num}",
            f"Session: {session_id}",
        )) + '\r\n'
        return response

    @classmethod
    def from_request(cls, request):
        match = re.match(
            r"(?P<request_type>\w+) rtsp://(?P<video_path>\S+) (?P<rtsp_version>RTSP/\d+.\d+)\r?\n"
            r"CSeq: (?P<seq_num>\d+)\r?\n"
            r"(Range: (?P<play_range>\w+=\d+-\d+\r?\n))?"
            r"(Transport: .*client_port=(?P<dst_port>\d+).*\r?\n)?"
            r"(Session: (?P<session_id>\d+)\r?\n)?",
            request.decode()
        )

        dic = match.groupdict()
        request_type = dic.get('request_type')

        video_path = dic.get('video_path')
        seq_num = dic.get('seq_num')
        dst_port = dic.get('dst_port')
        session_id = dic.get('session_id')

        if request_type == RTSPPacket.SETUP:
            dst_port = int(dst_port)
        sequence_number = int(seq_num)
        return cls(
            request_type,
            video_path,
            sequence_number,
            dst_port,
            session_id
        )

    def to_request(self):
        request_lines = [
            f"{self.request_type} rtsp://{self.video_path} {self.RTSP_VERSION}",
            f"CSeq: {self.sequence_number}",
        ]
        if self.request_type == RTSPPacket.SETUP:
            request_lines.append(
                f"Transport: RTP/UDP;client_port={self.dst_port}"
            )
        else:
            request_lines.append(
                f"Session: {self.session_id}"
            )
        request = '\r\n'.join(request_lines) + '\r\n'
        return request.encode()
# %%