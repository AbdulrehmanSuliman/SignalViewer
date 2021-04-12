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
        self.DynamicGraphList=[]
        self.ScrollBarList=[]
        self.SliderListOfLists = []
        self.SliderList = []
        self.sliderindex = 0
        self.tabIndex=0
        self.DynamicGraph=0
        self.Scrollbar=0
        self.isFirstTab=True

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

        
        self.main_widget = QtWidgets.QWidget(self)

        Layout = QtWidgets.QVBoxLayout(self.main_widget)

        self.Scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        
        self.WindowTab = QtWidgets.QTabWidget()
        self.AddTab()
        
        self.WindowTab.currentChanged.connect(self.TabChanged)

        Layout.addWidget(self.Toolbar)
        Layout.addWidget(self.WindowTab)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def fileQuit(self):
        self.close()

    def AddTab(self):
        
        self.addNewTab = QtWidgets.QWidget()
        self.TabLayout = QtWidgets.QHBoxLayout(self.addNewTab)
        self.GraphLayout = QtWidgets.QVBoxLayout(self.addNewTab)
        self.TabLayout.addLayout(self.GraphLayout)
        
        self.WindowTab.addTab(self.addNewTab, "Tab "+str(self.tabIndex+1))

        self.DynamicGraphList.append(MyDynamicMplCanvas(self.main_widget, width=5*2, height=4*2, dpi=100))

        self.ScrollBarList.append(QtWidgets.QScrollBar(QtCore.Qt.Horizontal))
        self.ScrollBarList[self.tabIndex].valueChanged.connect(lambda: self.ScrollAction())

        self.SliderList = []
        for i in range(10):
            self.SliderList.append(QtWidgets.QSlider(QtCore.Qt.Vertical))
            self.SliderList[i].setValue(20)
            self.SliderList[i].sliderPressed.connect(lambda: self.SliderPressed())
            self.SliderList[i].sliderReleased.connect(lambda: self.SliderReleased())
            self.SliderList[i].setTickPosition(QtWidgets.QSlider.TicksAbove)
            self.SliderList[i].setTickInterval(10)
        self.SliderListOfLists.append(self.SliderList)
        self.SliderLayout = QtWidgets.QGridLayout(self.addNewTab)
        self.SliderLayout.setHorizontalSpacing(20)
        self.SliderLayout.setVerticalSpacing(30) 

        self.GraphLayout.addWidget(self.DynamicGraphList[self.tabIndex])
        self.GraphLayout.addWidget(self.ScrollBarList[self.tabIndex])
        
        i = 0
        for x in range(2):
            for y in range(5):
                self.SliderLayout.addWidget(self.SliderList[i], x, y)
                i+=1
        self.TabLayout.addLayout(self.SliderLayout)
        
        # to be changed
        self.DynamicGraph=self.DynamicGraphList[self.tabIndex]
        self.Scrollbar=self.ScrollBarList[self.tabIndex]
        self.tabIndex += 1
    
    def SliderReleased(self):
        if self.sliderindex == 0:
            self.DynamicGraph.SliderChanged(0, self.SliderList[0].value()*(5/99))
        elif self.sliderindex == 1:
            self.DynamicGraph.SliderChanged(1, self.SliderList[1].value()*(5/99))
        elif self.sliderindex == 2:
            self.DynamicGraph.SliderChanged(2, self.SliderList[2].value()*(5/99))
        elif self.sliderindex == 3:
            self.DynamicGraph.SliderChanged(3, self.SliderList[3].value()*(5/99))
        elif self.sliderindex == 4:
            self.DynamicGraph.SliderChanged(4, self.SliderList[4].value()*(5/99))
        elif self.sliderindex == 5:
            self.DynamicGraph.SliderChanged(5, self.SliderList[5].value()*(5/99))
        elif self.sliderindex == 6:
            self.DynamicGraph.SliderChanged(6, self.SliderList[6].value()*(5/99))
        elif self.sliderindex == 7:
            self.DynamicGraph.SliderChanged(7, self.SliderList[7].value()*(5/99))
        elif self.sliderindex == 8:
            self.DynamicGraph.SliderChanged(8, self.SliderList[8].value()*(5/99))
        elif self.sliderindex == 9:
            self.DynamicGraph.SliderChanged(9, self.SliderList[9].value()*(5/99))
        

    def SliderPressed(self):    
        if self.SliderList[0].isSliderDown():
            self.sliderindex = 0
        elif self.SliderList[1].isSliderDown():
            self.sliderindex = 1
        elif self.SliderList[2].isSliderDown():
            self.sliderindex = 2
        elif self.SliderList[3].isSliderDown():
            self.sliderindex = 3
        elif self.SliderList[4].isSliderDown():
            self.sliderindex = 4
        elif self.SliderList[5].isSliderDown():
            self.sliderindex = 5
        elif self.SliderList[6].isSliderDown():
            self.sliderindex = 6
        elif self.SliderList[7].isSliderDown():
            self.sliderindex = 7
        elif self.SliderList[8].isSliderDown():
            self.sliderindex = 8
        elif self.SliderList[9].isSliderDown():
            self.sliderindex = 9

    def TabChanged(self):
        self.DynamicGraph = self.DynamicGraphList[self.WindowTab.currentIndex()]
        self.Scrollbar = self.ScrollBarList[self.WindowTab.currentIndex()]
        self.SliderList = self.SliderListOfLists[self.WindowTab.currentIndex()]
        
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
        self.DynamicGraph.setpageRight()
    def MoveLeft(self):
        self.DynamicGraph.setpageLeft()
    
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
        if self.isFirstTab ==False :
            self.AddTab()
        self.isFirstTab=False
        self.Scrollbar.setValue(99)
        self.DynamicGraph.SetTimeAndMagnitude(Time, Magnitude)
        self.DynamicGraph.SetTimer()

    def AddToPDF(self):
        screen=QtWidgets.QApplication.primaryScreen()
        screenshot=screen.grabWindow(self.winId())
        screenshot.save('photo.jpg','jpg')
        im = Image.open("photo.jpg")
        width, height = im.size
        left = 15
        top = height/5
        right = 820
        bottom = 3.75 * height / 4
        im1 = im.crop((left, top, right, bottom))
        newsize = (400, 220)
        im1 = im1.resize(newsize)
        if self.GraphsInPDF == 0:
            imagedata = [im1, 70, 490, 70,720,self.fname]
            self.ImageList.append(imagedata)
        elif self.GraphsInPDF == 1:
            imagedata = [im1,70, 245, 70, 470, self.fname]
            self.ImageList.append(imagedata)
        elif self.GraphsInPDF == 2:
            imagedata = [im1,70, 0, 70, 230, self.fname]
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

        for image,imgxcord,imgycord, namexcord, nameycord,GraphName in self.ImageList:  
            pdf.setFillColorRGB(0, 0, 0)    #subtitle
            pdf.setFont("Courier-Bold", 14)
            pdf.drawString(namexcord, nameycord, GraphName)
            pdf.drawInlineImage(image,imgxcord, imgycord)

        pdf.save()