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
        QtWidgets.QMainWindow.__init__(self)
        self.fname=""
        self.ImageList=[]
        self.GraphsInPDF = 0

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('File', self)
        self.file_menu.addAction('Open File', self.SelectFile, QtCore.Qt.CTRL + QtCore.Qt.Key_O)
        self.file_menu.addAction('Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.tools_menu = QtWidgets.QMenu('Tools', self)
        self.tools_menu.addAction('Stop/Play signal', self.stopSignal,QtCore.Qt.Key_Space)
        self.tools_menu.addAction('Zoom in', self.ZoomIn, QtCore.Qt.CTRL + QtCore.Qt.Key_Z)
        self.tools_menu.addAction('Zoom out', self.ZoomOut, QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_Z)
        self.tools_menu.addAction('Move Right', self.MoveRight, QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.tools_menu.addAction('Move Left', self.MoveLeft, QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.menuBar().addMenu(self.tools_menu)

        self.pdf_menu = QtWidgets.QMenu('PDF', self)
        self.pdf_menu.addAction('Add To PDF', self.AddToPDF, QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        self.pdf_menu.addAction('Create PDF', self.CreatePDF, QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_P)
        self.menuBar().addMenu(self.pdf_menu)

        self.Toolbar = QtWidgets.QToolBar()
        self.Toolbar.setIconSize(QtCore.QSize(30, 30))
        self.Toolbar.addAction(QIcon("image/open file.png"),"Open file", self.SelectFile)
        self.Toolbar.addSeparator()
        self.Toolbar.addAction(QIcon("image/pause.png"),"Pause signal", self.Pause)
        self.Toolbar.addAction(QIcon("image/play.png"),"Play signal", self.Start)
        self.Toolbar.addSeparator()
        self.Toolbar.addAction(QIcon("image/zoom in.png"),"Zoom in", self.ZoomIn)
        self.Toolbar.addAction(QIcon("image/zoom out.png"),"Zoom Out", self.ZoomOut)
        self.Toolbar.addAction(QIcon("image/arrow left.png"),"Move left", self.MoveLeft)
        self.Toolbar.addAction(QIcon("image/arrow right.png"),"Move right", self.MoveRight)
        self.Toolbar.addSeparator()
        self.Toolbar.addAction(QIcon("image/add to pdf.png"),"Add to PDF", self.AddToPDF)
        self.Toolbar.addAction(QIcon("image/create pdf.png"),"Create PDF", self.CreatePDF)

        self.main_widget = QtWidgets.QWidget    (self)

        Layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.DynamicGraph = MyDynamicMplCanvas(self.main_widget, width=5*2, height=4*2, dpi=100)
        self.Scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        self.Scrollbar.valueChanged.connect(lambda: self.ScrollAction())
        Layout.addWidget(self.Toolbar)
        Layout.addWidget(self.DynamicGraph)
        Layout.addWidget(self.Scrollbar)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def ScrollAction(self):
        self.DynamicGraph.ScrollUpdator(self.Scrollbar.value())

    def SetScrollbar(self, percentage):
        if percentage<0 or percentage>99:
            print ("Percentage is out of range")
            return

        self.Scrollbar.setValue(percentage)

    def closeEvent(self, ce):
        self.fileQuit()

    def stopSignal(self):
        self.DynamicGraph.SetIsStop()
    
    def Pause(self):
        self.DynamicGraph.PauseSignal()
    
    def Start(self):
        self.DynamicGraph.StartSignal()
    
    def ZoomIn(self):
        self.DynamicGraph.SetZoomFactor(True)

    def ZoomOut(self):
        self.DynamicGraph.SetZoomFactor(False)

    def MoveRight(self):
        self.DynamicGraph.SetScrollDisplacement(50)
    def MoveLeft(self):
        self.DynamicGraph.SetScrollDisplacement(-50)
    
    def open_dialog_box(self):
        filename = QFileDialog.getOpenFileName()
        path = filename[0]
        return path

    def SelectFile(self):
        path = self.open_dialog_box()
        if path == "":
            return
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
            imagedata = [im1, 70, 490, 70,720, 350,670, self.fname]
            self.ImageList.append(imagedata)
        elif self.GraphsInPDF == 1:
            imagedata = [im1,300, 220, 350, 460, 100, 400, self.fname]
            self.ImageList.append(imagedata)
        elif self.GraphsInPDF == 2:
            imagedata = [im1,70, 0, 70, 230, 350,150, self.fname]
            self.ImageList.append(imagedata)
        
        self.GraphsInPDF+=1
        
        
    def CreatePDF(self):
        fileName = 'Report.pdf'
        documentTitle = 'Report'
        pdf = canvas.Canvas(fileName)
        pdf.setTitle(documentTitle)
        pdfmetrics.registerFont( TTFont('abc', 'SakBunderan.ttf') )
        pdf.setFont('abc', 36)
        pdf.drawCentredString(300, 770, 'Report')   #title

        for image,imgxcord,imgycord, namexcord, nameycord, notesxcord, notesycord, GraphName in self.ImageList:  
            pdf.setFillColorRGB(0, 0, 0)    #subtitle
            pdf.setFont("Courier-Bold", 14)
            pdf.drawString(namexcord, nameycord, GraphName)
            pdf.drawString(notesxcord, notesycord, "Notes:-")
            pdf.drawInlineImage(image,imgxcord, imgycord)

        pdf.save()