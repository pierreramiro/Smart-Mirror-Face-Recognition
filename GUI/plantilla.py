import sys
from tkinter import Button
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recog.")
        self.resize(400, 600)
        # Create a QVBoxLayout instance
        layout = QVBoxLayout()
        # Add widgets to the layout
        #reamo button
        self.push_button_start=QPushButton("Start")
        self.push_button_start.height=100
        self.push_button_start.width=100
        layout.addWidget(self.push_button_start)
        # Set the layout on the application's window
        self.setLayout(layout)
        self.push_button_start.pressed.connect(self.buttonPressed)
    def buttonPressed(self):
        print("Hola")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_()) 