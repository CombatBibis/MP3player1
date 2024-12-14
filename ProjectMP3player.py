import sys
import os
import sounddevice as sd  # ��� ������ ��������������
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QSlider, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from pygame import mixer
from mutagen.mp3 import MP3

class MP3Player(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Player")
        self.setGeometry(300, 300, 600, 250)

        mixer.init()

        # ��������� ������� ���� � ����� ������
        self.setStyleSheet("background-color: black; color: white;")
        
        # �������� ���������� ����������
        self.select_button = QPushButton("������� MP3")
        self.select_button.setStyleSheet("background-color: gray; color: white;")
        self.select_button.clicked.connect(self.load_song)
        
        self.play_button = QPushButton("������")
        self.play_button.setStyleSheet("background-color: gray; color: white;")
        self.play_button.clicked.connect(self.play_song)
        
        self.pause_button = QPushButton("�����")
        self.pause_button.setStyleSheet("background-color: gray; color: white;")
        self.pause_button.clicked.connect(self.pause_song)
        
        self.stop_button = QPushButton("����")
        self.stop_button.setStyleSheet("background-color: gray; color: white;")
        self.stop_button.clicked.connect(self.stop_song)
        
        self.rewind_button = QPushButton("? -5 ���")
        self.rewind_button.setStyleSheet("background-color: gray; color: white;")
        self.rewind_button.clicked.connect(self.rewind)

        self.forward_button = QPushButton("? +5 ���")
        self.forward_button.setStyleSheet("background-color: gray; color: white;")
        self.forward_button.clicked.connect(self.forward)
        
        # ������ ��� ����������� ���������
        self.volume_down_button = QPushButton("��������� -")
        self.volume_down_button.setStyleSheet("background-color: gray; color: white;")
        self.volume_down_button.clicked.connect(self.decrease_volume)
        
        self.volume_up_button = QPushButton("��������� +")
        self.volume_up_button.setStyleSheet("background-color: gray; color: white;")
        self.volume_up_button.clicked.connect(self.increase_volume)

        # ����� ��� ����������� �������� �����
        self.track_label = QLabel("�������� �����: ��� �����")
        self.track_label.setStyleSheet("color: white; padding: 5px;")

        # ����� ��� ����������� �������
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")

        # �������� ��� ���������� ������� �������� �����
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderPressed.connect(self.start_manual_seek)
        self.slider.sliderReleased.connect(self.seek_position)

        # ������ ��� ���������� ��������
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)

        # ���������� ������ ��� ������ ���������� ������ �����
        self.output_device_combo = QComboBox()
        self.output_device_combo.addItems(self.get_audio_devices())
        self.output_device_combo.currentIndexChanged.connect(self.change_output_device)

        # ������ ����������
        layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        time_layout = QHBoxLayout()
        rewind_forward_layout = QHBoxLayout()
        volume_layout = QHBoxLayout()

        control_layout.addWidget(self.select_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)

        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(self.slider)
        time_layout.addWidget(self.total_time_label)

        rewind_forward_layout.addWidget(self.rewind_button)
        rewind_forward_layout.addWidget(self.forward_button)

        # ����������� ��������� � ����� ���������� ������
        volume_layout.addWidget(self.volume_down_button)
        volume_layout.addWidget(self.volume_up_button)
        volume_layout.addWidget(QLabel("���������� ������:"))
        volume_layout.addWidget(self.output_device_combo)

        layout.addWidget(self.track_label)
        layout.addLayout(control_layout)
        layout.addLayout(rewind_forward_layout)
        layout.addLayout(time_layout)
        layout.addLayout(volume_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # ���������� ��� �����
        self.filepath = ""
        self.song_length = 0
        self.playing = False
        self.seeking = False  # ���� ��� ������������ ������� ����������� ��������
        self.volume = 0.5  # ��������� ��������� (50%)
        mixer.music.set_volume(self.volume)

    def get_audio_devices(self):
        """�������� ������ ��������� ��������������."""
        devices = sd.query_devices()
        return [device['name'] for device in devices if device['max_output_channels'] > 0]

    def change_output_device(self, index):
        """������ ���������� ������ �����."""
        selected_device = self.output_device_combo.currentText()
        sd.default.device = selected_device

    def load_song(self):
        """��������� MP3-���� � �������� ��� �����, ��������� ��������."""
        self.filepath, _ = QFileDialog.getOpenFileName(self, "�������� MP3-����", "", "MP3 Files (*.mp3)")
        if self.filepath:
            try:
                self.track_label.setText(f"�������� �����: {os.path.basename(self.filepath)}")
                audio = MP3(self.filepath)
                self.song_length = int(audio.info.length)
                self.total_time_label.setText(self.format_time(self.song_length))
                self.slider.setRange(0, self.song_length)
            except Exception as e:
                self.track_label.setText("������ �������� �����")
                print(f"������: {e}")

    def play_song(self):
        """��������� ��������������� MP3 � ������� ������� ��������."""
        if self.filepath:
            try:
                mixer.music.load(self.filepath)
                mixer.music.play(start=self.slider.value())
                self.playing = True
                self.timer.start(1000)
            except Exception as e:
                print(f"������ ���������������: {e}")

    def pause_song(self):
        """������ �� ����� ��� ������������ ���������������."""
        if self.playing:
            mixer.music.pause()
            self.playing = False
        else:
            mixer.music.unpause()
            self.playing = True

    def stop_song(self):
        """������������� ���������������."""
        mixer.music.stop()
        self.playing = False
        self.timer.stop()
        self.slider.setValue(0)
        self.current_time_label.setText("00:00")

    def rewind(self):
        """������������ �� 5 ������ �����."""
        position = max(0, self.slider.value() - 5)
        self.slider.setValue(position)
        mixer.music.play(start=position)
    
    def forward(self):
        """������������ �� 5 ������ ������."""
        position = min(self.song_length, self.slider.value() + 5)
        self.slider.setValue(position)
        mixer.music.play(start=position)

    def update_slider(self):
        """��������� �������� � ����� �������� ���������������."""
        if self.playing and not self.seeking:
            current_time = mixer.music.get_pos() // 1000
            if current_time < self.song_length:
                self.slider.setValue(current_time)
                self.current_time_label.setText(self.format_time(current_time))
            else:
                self.stop_song()

    def start_manual_seek(self):
        """������������� ����, ��� ������������ ������� ���������� ��������."""
        self.seeking = True
    
    def seek_position(self):
        """������������ �� ��������� ��������� � �������� ��������������� � ������� �������."""
        if self.filepath:
            position = self.slider.value()
            mixer.music.load(self.filepath)
            mixer.music.play(start=position)
            self.playing = True
            self.seeking = False

    def decrease_volume(self):
        """��������� ���������."""
        self.volume = max(0, self.volume - 0.1)
        mixer.music.set_volume(self.volume)

    def increase_volume(self):
        """����������� ���������."""
        self.volume = min(1, self.volume + 0.1)  # ������������� �������� 100%
        mixer.music.set_volume(self.volume)

    def format_time(self, seconds):
        """����������� ����� � mm:ss."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes):02}:{int(seconds):02}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3Player()
    window.show()
    sys.exit(app.exec_())
