from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QSlider, QStyle
from PyQt5.QtGui import QPixmap, QIcon, QPalette
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
# from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PIL.ImageQt import ImageQt

from client.client import Client
from utils.video_streaming import VideoStreaming

IMG_DIR = "image/"


class ClientWindow(QMainWindow):
    _update_image_signal = pyqtSignal()

    def __init__(
            self,
            file_name,
            host_address,
            host_port,
            rtp_port,
            src_type,
            parent=None):
        super(ClientWindow, self).__init__(parent)
        self.video_player = QLabel()
        self.play_button = QPushButton()
        self.tear_button = QPushButton()

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.is_playing = False

        self._media_client = Client(
            file_name, host_address, host_port, rtp_port, src_type)

        self.slider = QSlider(Qt.Horizontal)    
        self.slider.setMinimum(0)
        self.slider.sliderMoved.connect(self.slider_moved)

        self._update_image_signal.connect(self.update_image)
        self._update_image_timer = QTimer()
        self._update_image_timer.timeout.connect(
            self._update_image_signal.emit)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 1024, 500)
        self.setWindowIcon(QIcon(IMG_DIR+"player.png"))

        # play Btn
        self.play_button.setEnabled(False)
        self.play_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.handle_play)

        self.tear_button.setEnabled(False)
        self.tear_button.setText('Teardown')
        self.tear_button.clicked.connect(self.handle_teardown)

        # slider
        #self.slider.setRange(0, self._media_client.total_frame_number)
        #self.slider.setRange(0, 500)

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # set widgets to the hbox layout
        hboxLayout.addWidget(self.play_button)
        hboxLayout.addWidget(self.slider)
        hboxLayout.addWidget(self.tear_button)

        # create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.video_player)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)

        central_widget = QVideoWidget(self)
        self.setCentralWidget(central_widget)

        central_widget.setLayout(vboxLayout)

        self.handle_setup()

    # def slider_moved(self, frame_num):
    #     #self._media_client.current_frame_number = frame_num
    #     frame = self._media_client.get_next_frame()
    #     if not frame : return
    #     pix = QPixmap.fromImage(ImageQt(frame[0]).copy())
    #     self.video_player.setPixmap(pix)

    def slider_moved(self, frame_num):
        self._media_client.current_frame_number = self.slider.value()
        frame = self._media_client.get_next_frame()
        if not frame : 
            ## TODO render loading image
            return
        pix = QPixmap.fromImage(ImageQt(frame[0]).copy())
        self.video_player.setPixmap(pix)

    def update_image(self):
        if not self._media_client.is_receiving_rtp:
            return
        self.slider.setRange(0, self._media_client.total_frame_number)
        self.slider_moved(self._media_client.current_frame_number)
        self.slider.setValue( self._media_client.current_frame_number )
        # frame = self._media_client.get_next_frame()
        # if frame is not None:
        #     pix = QPixmap.fromImage(ImageQt(frame[0]).copy())
        #     self.video_player.setPixmap(pix)
        #     print("current frame num =", self._media_client.current_frame_number)
        #     self.slider.setValue( int(self._media_client.current_frame_number) )
        #     # self.slider.setValue(int(
        #     #     self._media_client.current_frame_number/self._media_client.total_frame_number*1000))
        #     print("Slider value ",self.slider.value())

    def handle_setup(self):
        self._media_client.establish_rtsp_connection()
        self._media_client.send_setup_request()
        self.play_button.setEnabled(True)
        self.tear_button.setEnabled(True)
        self._update_image_timer.start(1000//VideoStreaming.FPS)

    def handle_play(self):
        if not self.is_playing:  # play request
            self._media_client.send_play_request()
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
            self.is_playing = True
        else:  # pause request
            self._media_client.send_pause_request()
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
            self.is_playing = False

    def handle_teardown(self):
        self._media_client.send_teardown_request()
        self.play_button.setEnabled(False)
        self._media_client.close_rtsp_connection()
        exit(0)
