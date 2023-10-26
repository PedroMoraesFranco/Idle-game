import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
import json

class IdleGame(QWidget):
    def __init__(self):
        super().__init__()
        self.ouro = 0
        self.ouro_por_segundo = 1
        self.tempo_ultimo_login = time.time()
        self.game_running = True
        self.showed_offline_notification = False

        self.initUI()
        self.loadSave()  # Carrega o progresso salvo automaticamente
        self.setupAutoSaveTimer()  # Inicia o temporizador de salvamento automático

    def initUI(self):
        self.setWindowTitle("Idle Game")
        self.setGeometry(100, 100, 400, 300)
        

        self.loadImages()
        self.createInterface()
        self.updateInterface()
        self.calculateOfflineEarnings()

    def loadImages(self):
        self.ouro_image = QPixmap("ouro.png")
        self.ouro_image = self.ouro_image.scaled(50, 50)

    def createInterface(self):
        layout = QVBoxLayout()

        self.ouro_label = QLabel()
        layout.addWidget(self.ouro_label)

        self.ouro_por_segundo_label = QLabel()
        layout.addWidget(self.ouro_por_segundo_label)

        self.melhorar_mina_button = QPushButton("Melhorar Mina (Custa 10 de ouro)")
        self.melhorar_mina_button.clicked.connect(self.upgradeMina)
        layout.addWidget(self.melhorar_mina_button)

        self.progress_label = QLabel("Progresso")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.quit_button = QPushButton("Sair")
        self.quit_button.clicked.connect(self.saveAndQuit)
        layout.addWidget(self.quit_button)

        self.restart_button = QPushButton("Reiniciar Jogo")
        self.restart_button.clicked.connect(self.restartGame)
        layout.addWidget(self.restart_button)

        self.save_button = QPushButton("Salvar Jogo")
        self.save_button.clicked.connect(self.saveProgress)
        layout.addWidget(self.save_button)

        self.load_button = QPushButton("Carregar Jogo Salvo")
        self.load_button.clicked.connect(self.loadProgress)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def updateInterface(self):
        self.ouro_label.setPixmap(self.ouro_image)
        self.ouro_label.setText(f"Ouro: {self.ouro}")
        self.ouro_por_segundo_label.setText(f"Ouro por segundo: {self.ouro_por_segundo}")

    def calculateOfflineEarnings(self):
        if self.game_running:
            tempo_atual = time.time()
            tempo_passado = tempo_atual - self.tempo_ultimo_login
            ouro_ganho_offline = self.ouro_por_segundo * tempo_passado
            self.ouro += ouro_ganho_offline

            if not self.showed_offline_notification and ouro_ganho_offline > 0:
                self.showNotification(f"Ganhou {int(ouro_ganho_offline)} de ouro offline!")
                self.showed_offline_notification = True

            self.tempo_ultimo_login = tempo_atual
            self.updateInterface()
            QTimer.singleShot(1000, self.calculateOfflineEarnings)

    def upgradeMina(self):
        if self.ouro >= 10:
            self.ouro -= 10
            self.ouro_por_segundo += 1
            self.updateInterface()

    def showNotification(self, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Notificação")
        msg_box.setText(message)
        msg_box.exec_()

    def restartGame(self):
        self.ouro = 0
        self.ouro_por_segundo = 1
        self.tempo_ultimo_login = time.time()
        self.showed_offline_notification = False
        self.updateInterface()

    def saveAndQuit(self):
        self.saveProgress()
        self.game_running = False
        sys.exit()

    def saveProgress(self):
        progress = {
            "ouro": self.ouro,
            "ouro_por_segundo": self.ouro_por_segundo
        }
        with open("progress.json", "w") as file:
            json.dump(progress, file)

    def loadSave(self):
        try:
            with open("progress.json", "r") as file:
                progress = json.load(file)
                self.ouro = progress["ouro"]
                self.ouro_por_segundo = progress["ouro_por_segundo"]
        except FileNotFoundError:
            pass

    def loadProgress(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Carregar Jogo Salvo", "", "JSON Files (*.json)", options=options)
        if file_name:
            with open(file_name, "r") as file:
                progress = json.load(file)
                self.ouro = progress["ouro"]
                self.ouro_por_segundo = progress["ouro_por_segundo"]
            self.updateInterface()

    def setupAutoSaveTimer(self):
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.saveProgress)
        self.auto_save_timer.start(1000)  # Configura o temporizador para acionar a cada 10 segundos

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = IdleGame()
    game.show()
    sys.exit(app.exec_())
