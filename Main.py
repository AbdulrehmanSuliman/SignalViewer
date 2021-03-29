from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 500, 500)
        self.setWindowTitle("Signal Viewer")
       self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("A7A EL4B4B DA3")
        self.label.move(100, 300)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Mtdos 3lya ysta")
        self.b1.clicked.connect(self.clickedb1)

    def clickedb1(self):
        self.label.setText("enta dost gamed ysta")
        self.update()
    
    def update(self):
        self.label.adjustSize()




def window():
    app = QApplication(sys.argv)
    win = MyWindow()


    win.show()
    sys.exit(app.exec_())

window()