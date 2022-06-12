import sys
import time

from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout,QLabel


class warningBox (QDialog):
    def __init__(self,parent=None):
        super(warningBox,self).__init__(parent)
        #nombre a la ventana
        self.setWindowTitle("HELLO!")
        #Creo un layout
        self.layout = QVBoxLayout()
        # loading image
        image = QImage('resources/facePostions.jpeg')
        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.layout.addWidget(self.imageLabel)
        # Configuramos el layout
        self.setLayout(self.layout)

        self.timer=QTimer()
        self.timer.timeout.connect(self.CloseWarning)
        self.timer.start(1000)
        
    def CloseWarning(self):
        print("cerrando")
        self.close()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self, s):
        print("click", s)

        dlg = warningBox(self)
        dlg.show()
        


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()