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
            file_name: str,
            host_address: str,
            host_port: int,
            rtp_port: int,
            parent=None):
        super(ClientWindow, self).__init__(parent)
        self.video_player = QLabel()
        #self.video_player = QVideoWidget()
        self.setup_button = QPushButton()
        self.play_button = QPushButton()
        self.tear_button = QPushButton()
        self.error_label = QLabel()

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.is_playing = False
        self.slider = QSlider(Qt.Horizontal)

        self._media_client = Client(file_name, host_address, host_port, rtp_port)
        self._update_image_signal.connect(self.update_image)
        self._update_image_timer = QTimer()
        self._update_image_timer.timeout.connect(self._update_image_signal.emit)


        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 1024, 500)
        self.setWindowIcon(QIcon(IMG_DIR+"player.png"))

        # slider
        self.slider.setRange(0, 0)

        self.setup_button.setEnabled(True)
        self.setup_button.setText('Setup')
        self.setup_button.clicked.connect(self.handle_setup)

        # play Btn
        self.play_button.setEnabled(False)
        self.play_button.setIcon( self.style().standardIcon(QStyle.SP_MediaPlay) )
        self.play_button.clicked.connect(self.handle_play)


        self.tear_button.setEnabled(False)
        self.tear_button.setText('Teardown')
        self.tear_button.clicked.connect(self.handle_teardown)

        self.error_label.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Maximum)

        

        # slider
        self.slider.setRange(0,0)

        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        #create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0,0,0,0)
 
        #set widgets to the hbox layout
        hboxLayout.addWidget(self.setup_button)
        hboxLayout.addWidget(self.play_button)
        hboxLayout.addWidget(self.slider)
        hboxLayout.addWidget(self.tear_button)

        #create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(self.video_player)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)

        central_widget = QVideoWidget(self)
        self.setCentralWidget(central_widget)

        central_widget.setLayout(vboxLayout)


    def update_image(self):
        if not self._media_client.is_receiving_rtp:
            return
        frame = self._media_client.get_next_frame()
        if frame is not None:
            pix = QPixmap.fromImage(ImageQt(frame[0]).copy())
            self.video_player.setPixmap(pix)

    def handle_setup(self):
        self._media_client.establish_rtsp_connection()
        self._media_client.send_setup_request()
        self.setup_button.setEnabled(False)
        self.play_button.setEnabled(True)
        self.tear_button.setEnabled(True)
        self._update_image_timer.start(1000//VideoStreaming.FPS)

    def handle_play(self):
        if not self.is_playing: ## play request
            self._media_client.send_play_request()
            self.play_button.setIcon( self.style().standardIcon(QStyle.SP_MediaPause) )
            self.is_playing = True
        else:                   ## pause request
            self._media_client.send_pause_request()
            self.play_button.setIcon( self.style().standardIcon(QStyle.SP_MediaPlay) )
            self.is_playing = False

    def handle_teardown(self):
        self._media_client.send_teardown_request()
        self.setup_button.setEnabled(True)
        self.play_button.setEnabled(False)
        exit(0)

    def handle_error(self):
        self.play_button.setEnabled(False)
        self.tear_button.setEnabled(False)
        self.error_label.setText(f"Error: {self.media_player.errorString()}")

