import os, cv2
READ_CHUNK_SIZE = 1024
EXPECTED_FRAME_SIZE = 100000

class VideoStreaming:
    #  FRAME_HEADER_LENGTH = 5
    FPS = 24
    JPEG_EOF = b'\xff\xd9'

    def __init__(self, file_path, src_type): # src_type = 'file' or 'webcam'
        self.type = src_type
        if self.type == 'file':
            self.video = open(file_path, 'rb')
            self.video_length = 0
            self.current_frame_number = -1

            ## legacy mjpeg reader
            #  while True:
            #      try:
            #          frame_length = self.video.read(self.FRAME_HEADER_LENGTH)
            #          if len(frame_length) != 5:
            #              if frame_length:
            #                  raise ValueError
            #              else:
            #                  break
            #      except ValueError:
            #          print('wrong file format')
            #          break
            #      frame_length = int(frame_length.decode())
            #      frame = self.video.read(frame_length)
            #      self.video_length += 1
            #self.video_length = os.path.getsize(file_path)//(5+bytes_per_frame)

            ## slightly improved mjpeg reader

            endmark = 0
            count = 0

            s = self.video.read(READ_CHUNK_SIZE)
            tmpbyte = s[-1:]

            while True:
                startmark = (tmpbyte+s).find(b'\xff\xd8', endmark)
                while startmark == -1 and s != b'':
                    s = self.video.read(READ_CHUNK_SIZE)
                    startmark = (tmpbyte+s).find(b'\xff\xd8')
                    tmpbyte = s[-1:]
                if s == b'':
                    break

                s = (tmpbyte+s)[startmark:] + self.video.read(EXPECTED_FRAME_SIZE)

                endmark = s.find(b'\xff\xd9')
                if endmark == -1:
                    raise Exception('bad expected frame size size')
                vid = s[:endmark+2]

                count += 1

            self.video_length = count
            self.video.seek(0, os.SEEK_SET)
            self.vid_buffer = self.video.read(READ_CHUNK_SIZE)
            self.vid_tmp_byte = self.vid_buffer[-1]
            self.last_endmark = 0

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
        startmark = (bytes([self.vid_tmp_byte])+self.vid_buffer).find(b'\xff\xd8', self.last_endmark)
        while startmark == -1 and self.vid_buffer != b'':
            self.vid_buffer = self.video.read(READ_CHUNK_SIZE)
            startmark = (bytes([self.vid_tmp_byte])+self.vid_buffer).find(b'\xff\xd8')
            self.vid_tmp_byte = self.vid_buffer[-1:]
        if self.vid_buffer == b'':
            # reached EOF
            return None

        self.vid_buffer = (bytes([self.vid_tmp_byte])+self.vid_buffer)[startmark:] + \
                self.video.read(EXPECTED_FRAME_SIZE)

        self.last_endmark = self.vid_buffer.find(b'\xff\xd9')
        if self.last_endmark == -1:
            raise Exception('bad size')

        self.current_frame_number += 1

        return self.vid_buffer[:self.last_endmark+2]

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
