from MainWindow import Ui_MainWindow
import sys
from PyQt5 import QtWidgets

class mirrollGUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        #Creamos nuestra GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #Establecemos info por defecto
        self.fecha_actual="viernes, 10 de junio del 2022"
        self.hora_actual="18:00 pm"
        self.temperatura_actual="00"
        self.ui.temperatura.setText(self.temperatura_actual)   

stylesheet="""
    QMainWindow{
        background:black
    }
"""

#Creamos la app
app = QtWidgets.QApplication(sys.argv)  
#Colocamos background
app.setStyleSheet(stylesheet)
#Creamos el visualizador, solo la pantalla
mirrolGUI_window=mirrollGUI()
mirrolGUI_window.show()                        
sys.exit(app.exec_())
