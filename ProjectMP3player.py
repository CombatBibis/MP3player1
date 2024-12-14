import sys
import os
import sounddevice as sd  # Для списка аудиоустройств
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

        # Установка чёрного фона и серых кнопок
        self.setStyleSheet("background-color: black; color: white;")
        
        # Основные компоненты интерфейса
        self.select_button = QPushButton("Выбрать MP3")
        self.select_button.setStyleSheet("background-color: gray; color: white;")
        self.select_button.clicked.connect(self.load_song)
        
        self.play_button = QPushButton("Играть")
        self.play_button.setStyleSheet("background-color: gray; color: white;")
        self.play_button.clicked.connect(self.play_song)
        
        self.pause_button = QPushButton("Пауза")
        self.pause_button.setStyleSheet("background-color: gray; color: white;")
        self.pause_button.clicked.connect(self.pause_song)
        
        self.stop_button = QPushButton("Стоп")
        self.stop_button.setStyleSheet("background-color: gray; color: white;")
        self.stop_button.clicked.connect(self.stop_song)
        
        self.rewind_button = QPushButton("? -5 сек")
        self.rewind_button.setStyleSheet("background-color: gray; color: white;")
        self.rewind_button.clicked.connect(self.rewind)

        self.forward_button = QPushButton("? +5 сек")
        self.forward_button.setStyleSheet("background-color: gray; color: white;")
        self.forward_button.clicked.connect(self.forward)
        
        # Кнопки для регулировки громкости
        self.volume_down_button = QPushButton("Громкость -")
        self.volume_down_button.setStyleSheet("background-color: gray; color: white;")
        self.volume_down_button.clicked.connect(self.decrease_volume)
        
        self.volume_up_button = QPushButton("Громкость +")
        self.volume_up_button.setStyleSheet("background-color: gray; color: white;")
        self.volume_up_button.clicked.connect(self.increase_volume)

        # Метка для отображения названия трека
        self.track_label = QLabel("Название трека: Нет файла")
        self.track_label.setStyleSheet("color: white; padding: 5px;")

        # Метки для отображения времени
        self.current_time_label = QLabel("00:00")
        self.total_time_label = QLabel("00:00")

        # Ползунок для управления текущей позицией трека
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderPressed.connect(self.start_manual_seek)
        self.slider.sliderReleased.connect(self.seek_position)

        # Таймер для обновления ползунка
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)

        # Выпадающий список для выбора устройства вывода звука
        self.output_device_combo = QComboBox()
        self.output_device_combo.addItems(self.get_audio_devices())
        self.output_device_combo.currentIndexChanged.connect(self.change_output_device)

        # Сборка интерфейса
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

        # Регулировка громкости и выбор устройства вывода
        volume_layout.addWidget(self.volume_down_button)
        volume_layout.addWidget(self.volume_up_button)
        volume_layout.addWidget(QLabel("Устройство вывода:"))
        volume_layout.addWidget(self.output_device_combo)

        layout.addWidget(self.track_label)
        layout.addLayout(control_layout)
        layout.addLayout(rewind_forward_layout)
        layout.addLayout(time_layout)
        layout.addLayout(volume_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Переменные для трека
        self.filepath = ""
        self.song_length = 0
        self.playing = False
        self.seeking = False  # Флаг для отслеживания ручного перемещения ползунка
        self.volume = 0.5  # Начальная громкость (50%)
        mixer.music.set_volume(self.volume)

    def get_audio_devices(self):
        """Получает список доступных аудиоустройств."""
        devices = sd.query_devices()
        return [device['name'] for device in devices if device['max_output_channels'] > 0]

    def change_output_device(self, index):
        """Меняет устройство вывода звука."""
        selected_device = self.output_device_combo.currentText()
        sd.default.device = selected_device

    def load_song(self):
        """Загружает MP3-файл и получает его длину, обновляет название."""
        self.filepath, _ = QFileDialog.getOpenFileName(self, "Выберите MP3-файл", "", "MP3 Files (*.mp3)")
        if self.filepath:
            try:
                self.track_label.setText(f"Название трека: {os.path.basename(self.filepath)}")
                audio = MP3(self.filepath)
                self.song_length = int(audio.info.length)
                self.total_time_label.setText(self.format_time(self.song_length))
                self.slider.setRange(0, self.song_length)
            except Exception as e:
                self.track_label.setText("Ошибка загрузки файла")
                print(f"Ошибка: {e}")

    def play_song(self):
        """Запускает воспроизведение MP3 с текущей позиции ползунка."""
        if self.filepath:
            try:
                mixer.music.load(self.filepath)
                mixer.music.play(start=self.slider.value())
                self.playing = True
                self.timer.start(1000)
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")

    def pause_song(self):
        """Ставит на паузу или возобновляет воспроизведение."""
        if self.playing:
            mixer.music.pause()
            self.playing = False
        else:
            mixer.music.unpause()
            self.playing = True

    def stop_song(self):
        """Останавливает воспроизведение."""
        mixer.music.stop()
        self.playing = False
        self.timer.stop()
        self.slider.setValue(0)
        self.current_time_label.setText("00:00")

    def rewind(self):
        """Перематывает на 5 секунд назад."""
        position = max(0, self.slider.value() - 5)
        self.slider.setValue(position)
        mixer.music.play(start=position)
    
    def forward(self):
        """Перематывает на 5 секунд вперед."""
        position = min(self.song_length, self.slider.value() + 5)
        self.slider.setValue(position)
        mixer.music.play(start=position)

    def update_slider(self):
        """Обновляет ползунок и время текущего воспроизведения."""
        if self.playing and not self.seeking:
            current_time = mixer.music.get_pos() // 1000
            if current_time < self.song_length:
                self.slider.setValue(current_time)
                self.current_time_label.setText(self.format_time(current_time))
            else:
                self.stop_song()

    def start_manual_seek(self):
        """Устанавливает флаг, что пользователь вручную перемещает ползунок."""
        self.seeking = True
    
    def seek_position(self):
        """Перематывает на выбранное положение и начинает воспроизведение с текущей позиции."""
        if self.filepath:
            position = self.slider.value()
            mixer.music.load(self.filepath)
            mixer.music.play(start=position)
            self.playing = True
            self.seeking = False

    def decrease_volume(self):
        """Уменьшает громкость."""
        self.volume = max(0, self.volume - 0.1)
        mixer.music.set_volume(self.volume)

    def increase_volume(self):
        """Увеличивает громкость."""
        self.volume = min(1, self.volume + 0.1)  # Устанавливаем максимум 100%
        mixer.music.set_volume(self.volume)

    def format_time(self, seconds):
        """Форматирует время в mm:ss."""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes):02}:{int(seconds):02}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MP3Player()
    window.show()
    sys.exit(app.exec_())
