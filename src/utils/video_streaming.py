import os


class VideoStreaming:
    FRAME_HEADER_LENGTH = 5
    FPS = 24
    JPEG_EOF = b'\xff\xd9'

    def __init__(self, file_path):
        self.video = open(file_path, 'rb')
        self.video_length = 0
        self.current_frame_number = -1
        while True:
            try:
                frame_length = self.video.read(self.FRAME_HEADER_LENGTH)
                if len(frame_length) != 5:
                    if frame_length:
                        raise ValueError
                    else:
                        break
            except ValueError:
                print('wrong file format')
                break
            frame_length = int(frame_length.decode())
            frame = self.video.read(frame_length)
            self.video_length += 1
        #self.video_length = os.path.getsize(file_path)//(5+bytes_per_frame)
        self.video.seek(0, os.SEEK_SET)

    def get_next_frame(self):
        try:
            frame_length = self.video.read(self.FRAME_HEADER_LENGTH)
            if len(frame_length) != 5:
                if frame_length:
                    raise ValueError
                else:
                    return None
        except ValueError:
            return None

        frame_length = int(frame_length.decode())
        frame = self.video.read(frame_length)
        self.current_frame_number += 1
        return bytes(frame)

    def close(self):
        self.video.close()
