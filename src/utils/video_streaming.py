import os, cv2

class VideoStreaming:
    FRAME_HEADER_LENGTH = 5
    FPS = 24
    JPEG_EOF = b'\xff\xd9'

    def __init__(self, file_path, src_type='file'): # src_type = 'file' or 'webcam'
        self.type = src_type
        if self.type == 'file':
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
        elif self.type == 'webcam':
            self.cap = cv2.VideoCapture(0)
            self.video_length = 1
            self.current_frame_number = -1
        else:
            raise Exception('Unsupported source type.')

    def get_next_frame(self):
        if self.type == 'file':
            return self._get_next_frame_from_file()
        elif self.type == 'webcam':
            return self._get_next_frame_from_webcam()
        else:
            raise Exception('Unsupported source type.')


    def _get_next_frame_from_file(self):
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

    def _get_next_frame_from_webcam(self):
        ret, frame = self.cap.read()
        self.current_frame_number += 1
        return cv2.imencode('.jpg', frame)[1].tostring()

    def close(self):
        if self.type == 'file':
            self.video.close()
        elif self.type == 'webcam':
            self.cap.release()
        else:
            raise Exception('Unsupported source type.')
