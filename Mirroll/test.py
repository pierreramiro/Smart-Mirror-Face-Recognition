import sys
import time

from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QVBoxLayout,QLabel

dato=1

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
        global dato
        print("cerrando")
        time.sleep(2)
        parent=self.parent()
        dato+=2
        parent.dato=dato
        print("Valor despues de crear la notificacion: ",parent.dato)
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

    def button_clicked(self, s):
        print("click", s)
        print("Valor antes de cerrar la notificacion: ",self.dato)
        dlg = warningBox(self)
        dlg.show()
        


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()



"""
Trama como admin(usuario) 
[funcion,id usuario,color,BINtomacorriente]
[2,3,rojo,101]

Trama como usuario básico
[funcion,id usuario,color]
[1,3,azul]

Trama configurar rostro
[funcion,id usuario]
[0,1]
"""