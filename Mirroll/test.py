import sys
import time

from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout,QLabel

dato=1

class sleepModeDialog(QDialog):
    def __init__(self,parent=None,val=0):
        super(sleepModeDialog,self).__init__(parent)
        self.val=val
        #nombre a la ventana
        self.setWindowTitle("Sleep!")
        #Creo un layout
        self.layout = QVBoxLayout()
        # loading image
        image = QImage('resources/RFLogo.png')
        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.layout.addWidget(self.imageLabel)
        # Configuramos el layout
        self.setLayout(self.layout)
        self.timer=QTimer()
        self.timer.timeout.connect(self.initClass)
        self.timer.start(1000)
        self.parent().newVal=11

    def initClass(self):
        self.timer.stop()
        for i in range(5):
            time.sleep(1)
            print("Tiempo transcurrido:",i)
        time.sleep(1)
        print("Cerramos el sleep")
        self.close()
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

class warningBox (QDialog):
    def __init__(self,parent=None,val=0):
        super(warningBox,self).__init__(parent)
        self.val=val
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
        print("Valor despues de crear la notificacion: ",self.val)
        self.parent().imprime()
        self.close()
    
    def closeEvent(self, event):
        self.timer.stop()
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("My App")
        self.dato=dato
        button = QPushButton("Press me for a dialog!")
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)
        self.startVal=True
        self.time1=QTimer()
        self.time1.timeout.connect(self.initMirroll)
        self.time1.start(10)

    def initMirroll(self):
        self.time1.stop()
        dlg = sleepModeDialog(self)
        dlg.show()
        

    def button_clicked(self, s):
        print("click", s)
        print("Valor antes de cerrar la notificacion: ",self.newVal)
        dlg = warningBox(self,val=5)
        dlg.show()
    def imprime(self):
        print("Hola Pierre")



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()


