class VideoStreaming:
    FRAME_HEADER_LENGTH = 5
    FPS = 24
    JPEG_EOF = b'\xff\xd9'

    def __init__(self, file_path):
        self.video = open(file_path, 'rb')
        self.current_frame_number = -1

    def get_next_frame(self):
        try:
            frame_length = self.video.read(self.FRAME_HEADER_LENGTH)
        except ValueError:
            raise EOFError
        frame_length = int(frame_length.decode())
        frame = self.video.read(frame_length)
        self.current_frame_number += 1
        return bytes(frame)

    def close(self):
        self.video.close()
