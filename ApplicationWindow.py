from DynamicGraph import MyDynamicMplCanvas
import numpy as np

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QApplication
from PyQt5.QtGui import *

from PIL import Image
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.fname=""
        self.ImageList=[]
        self.GraphsInPDF = 0
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('File', self)
        self.file_menu.addAction('Browse File', self.SelectFile, QtCore.Qt.CTRL + QtCore.Qt.Key_B)
        self.file_menu.addAction('Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.tools_menu = QtWidgets.QMenu('Tools', self)
        self.tools_menu.addAction('Stop/Play signal', self.stopSignal,QtCore.Qt.Key_Space)
        self.tools_menu.addAction('Zoom in', self.ZoomIn,QtCore.Qt.Key_Z)
        self.tools_menu.addAction('Zoom out', self.ZoomOut,QtCore.Qt.Key_O)
        self.tools_menu.addAction('Move Right', self.MoveRight, QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.tools_menu.addAction('Move Left', self.MoveLeft, QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.menuBar().addMenu(self.tools_menu)

        self.pdf_menu = QtWidgets.QMenu('PDF', self)
        self.pdf_menu.addAction('Add To PDF', self.AddToPDF, QtCore.Qt.CTRL + QtCore.Qt.Key_D)
        self.pdf_menu.addAction('Create PDF', self.CreatePDF, QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        self.menuBar().addMenu(self.pdf_menu)

        self.main_widget = QtWidgets.QWidget(self)

        Layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.DynamicGraph = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        Layout.addWidget(self.DynamicGraph)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def stopSignal(self):
        self.DynamicGraph.SetIsStop()

    def ConSignal(self):
        self.DynamicGraph.SetIsStop()
        
    def ZoomIn(self):
        self.DynamicGraph.SetZoomFactor(True)
    def ZoomOut(self):
        self.DynamicGraph.SetZoomFactor(False)

    def MoveRight(self):
        self.DynamicGraph.SetScrollDisplacement(100)
    def MoveLeft(self):
        self.DynamicGraph.SetScrollDisplacement(-100)
    
    def open_dialog_box(self):
        filename = QFileDialog.getOpenFileName()
        path = filename[0]
        return path

    def SelectFile(self):
        path = self.open_dialog_box()
        print(path)
        i=0
        FileName = ""
        while path[i] != "." or path[i+1] != "t" or path[i+2] != "x" or path[i+3] != "t":
            if path[i] == '/':
                FileName =""
            else:
                FileName = FileName + path[i]
            i=i+1
        self.fname=FileName
        Time,trash, Magnitude = np.loadtxt(path,unpack=True)

        self.DynamicGraph.SetTimeAndMagnitude(Time, Magnitude)
        self.DynamicGraph.SetTimer()

    def AddToPDF(self):
        screen=QtWidgets.QApplication.primaryScreen()
        screenshot=screen.grabWindow(self.winId())
        screenshot.save('photo.jpg','jpg')
        im = Image.open("photo.jpg")
        width, height = im.size
        left = 10
        top = height/8
        right = 500
        bottom = 3.75 * height / 4
        im1 = im.crop((left, top, right, bottom))
        newsize = (220, 220)
        im1 = im1.resize(newsize)
        if self.GraphsInPDF == 0:
            imagedata = [im1, 70, 490]
        elif self.GraphsInPDF == 1:
            imagedata = [im1,300, 220]
        elif self.GraphsInPDF == 2:
            imagedata = [im1,70, 0]
        
        self.GraphsInPDF+=1
        self.ImageList.append(imagedata)
        
        
    def CreatePDF(self):
        fileName = 'Report.pdf'
        documentTitle = 'Report'
        pdf = canvas.Canvas(fileName)
        pdf.setTitle(documentTitle)
        pdfmetrics.registerFont( TTFont('abc', 'SakBunderan.ttf') )
        pdf.setFont('abc', 36)
        pdf.drawCentredString(300, 770, 'Report')   #title

        for image,xcord,ycord in self.ImageList:
            print(xcord)  
            pdf.setFillColorRGB(0, 0, 0)    #subtitle
            pdf.setFont("Courier-Bold", 14)
            pdf.drawString(70,720, self.fname)
            pdf.drawString(350,670, "Notes:-")
            # pdf.line(70, 715, 140, 715)
            pdf.drawInlineImage(image,xcord, ycord)

        pdf.save()