from DynamicGraph import MyDynamicMplCanvas
from DynamicGraph import *
from matplotlib.backends.backend_pdf import PdfPages 

import numpy as np

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QApplication
from PyQt5.QtGui import *

from PIL import Image
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from matplotlib import pyplot as plt
from scipy.io.wavfile import write
#from playsound import playsound
import simpleaudio as sa 


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.fname=""
        self.ImageList=[]
        self.GraphsInPDF = 0
        self.DynamicGraphList=[]
        self.ScrollBarList=[]
        self.SliderListOfLists = []
        self.SpectroSliderListOfLists = []
        self.SliderMapperResetList = []
        self.SliderResetListOfLists = []
        self.SliderResetList = []
        self.SliderList = []
        self.sliderindex = 0
        self.Spectrosliderindex = 0
        self.tabIndex=0
        self.DynamicGraph=0
        self.Scrollbar=0
        self.isFirstTab=True

        self.xDataToPdf=[]
        self.xDataToPdfOut=[]
        self.yDataToPdf=[]
        self.yDataToPdfOut=[]
        self.GraphCollection=[]
        
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
        self.Toolbar.addSeparator()
        #self.Toolbar.addAction(QIcon("image/add to pdf.png"),"Testing Signal", self.validationSignal)
        self.Toolbar.addAction(QIcon("image/audio icon.png"),"Play sound", self.playAudio)

        
        self.main_widget = QtWidgets.QWidget(self)

        Layout = QtWidgets.QVBoxLayout(self.main_widget)

        self.Scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Horizontal)
        self.ResetSignalMapper = QtCore.QSignalMapper() 
        
        self.WindowTab = QtWidgets.QTabWidget()
        self.WindowTab.setTabsClosable(True)
        self.WindowTab.tabCloseRequested.connect(self.CloseTab)
        self.AddTab()
        
        self.WindowTab.currentChanged.connect(self.TabChanged)

        Layout.addWidget(self.Toolbar)
        Layout.addWidget(self.WindowTab)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)


        #validation signal
        
   
    def fileQuit(self):
        self.close()

    def CloseTab(self, index):
        # self.DynamicGraph = self.DynamicGraphList[self.WindowTab.currentIndex()]
        # self.Scrollbar = self.ScrollBarList[self.WindowTab.currentIndex()]
        # self.SliderList = self.SliderListOfLists[self.WindowTab.currentIndex()]
        # self.SpectroSliderList = self.SpectroSliderListOfLists[self.WindowTab.currentIndex()]
        # self.SliderResetList = self.SliderResetListOfLists[self.WindowTab.currentIndex()]
        # self.ResetSignalMapper = self.SliderMapperResetList[self.WindowTab.currentIndex()]
        self.DynamicGraphList.pop(index)
        self.ScrollBarList.pop(index)
        self.SliderListOfLists.pop(index)
        self.SpectroSliderListOfLists.pop(index)
        self.SliderResetListOfLists.pop(index)
        self.SliderMapperResetList.pop(index)
        self.WindowTab.removeTab(index)
        self.TabChanged()

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
        self.SliderResetList = []
        self.ResetSignalMapper = QtCore.QSignalMapper()
        for i in range(10):
            self.SliderList.append(QtWidgets.QSlider(QtCore.Qt.Vertical))
            self.SliderList[i].setValue(20)
            self.SliderList[i].sliderPressed.connect(lambda: self.SliderPressed())
            self.SliderList[i].sliderReleased.connect(lambda: self.SliderReleased())
            self.SliderList[i].setTickPosition(QtWidgets.QSlider.TicksAbove)
            self.SliderList[i].setTickInterval(10)
            self.SliderResetList.append(QtWidgets.QPushButton("Reset"))
            self.SliderResetList[i].setFixedWidth(45)
            self.SliderResetList[i].clicked.connect(self.ResetSignalMapper.map)
            self.ResetSignalMapper.setMapping(self.SliderResetList[i], i)
        self.ResetSignalMapper.mapped.connect(self.ResetButtonClicked)
        self.SliderMapperResetList.append(self.ResetSignalMapper)
        self.SliderResetListOfLists.append(self.SliderResetList)
        self.SliderListOfLists.append(self.SliderList)

        self.SliderLayout = QtWidgets.QGridLayout(self.addNewTab)
        self.SliderLayout.setHorizontalSpacing(20)
        #self.SliderLayout.setVerticalSpacing(30)

        self.PanelsLayout = QtWidgets.QVBoxLayout(self.addNewTab)
        self.PanelsLayout.addWidget(QtWidgets.QLabel("Output Signal Controls"))
        self.PanelsLayout.addLayout(self.SliderLayout)
        
        self.PanelsLayout.addWidget(QtWidgets.QLabel("Spectrogram Controls"))
        self.SpectroComboBox = QtWidgets.QComboBox()
        self.SpectroComboBox.addItems(['default', 'plasma', 'inferno', 'magma', 'cividis'])
        self.SpectroComboBox.currentIndexChanged.connect(lambda: self.SpectroColorChanged())
        self.PanelsLayout.addWidget(self.SpectroComboBox)

        self.SpectroSliderList = []
        self.SpectroSliderLayout = QtWidgets.QHBoxLayout()
        for i in range(2):
            self.SpectroSliderList.append(QtWidgets.QSlider(QtCore.Qt.Vertical))
            self.SpectroSliderList[i].setFixedHeight(200)
            self.SpectroSliderList[i].sliderPressed.connect(lambda: self.SpectroSliderPressed())
            self.SpectroSliderList[i].sliderReleased.connect(lambda: self.SpectroSliderReleased())
            self.SpectroSliderList[i].setTickPosition(QtWidgets.QSlider.TicksAbove)
            self.SpectroSliderList[i].setTickInterval(10)
            self.SpectroSliderLayout.addWidget(self.SpectroSliderList[i])
        self.SpectroSliderList[1].setValue(99)
        self.SpectroSliderListOfLists.append(self.SpectroSliderList)
        self.PanelsLayout.addLayout(self.SpectroSliderLayout)

        self.GraphLayout.addWidget(self.DynamicGraphList[self.tabIndex])
        self.GraphLayout.addWidget(self.ScrollBarList[self.tabIndex])
        
        i = 0
        for x in range(2):
            for y in range(5):
                self.SliderLayout.addWidget(self.SliderList[i], 2*x, y)
                self.SliderLayout.addWidget(self.SliderResetList[i],2*x+1, y)
                i+=1
        self.TabLayout.addLayout(self.PanelsLayout)
        
        # to be changed
        self.DynamicGraph=self.DynamicGraphList[self.tabIndex]
        self.Scrollbar=self.ScrollBarList[self.tabIndex]
        self.WindowTab.setCurrentIndex(self.tabIndex)
        self.tabIndex += 1

    def ResetButtonClicked(self, index):
        self.SliderList[index].setValue(20)
        self.DynamicGraph.SliderChanged(index, self.SliderList[index].value()*(5/99))
    
    def SpectroColorChanged(self):
        self.DynamicGraph.ChangeSpectroColor(self.SpectroComboBox.currentIndex())

    def SpectroSliderReleased(self):
        self.DynamicGraph.SpectroSliderChanged(self.Spectrosliderindex, self.SpectroSliderList[self.Spectrosliderindex].value())
            

    def SpectroSliderPressed(self):
        for index in range(2):
            if self.SpectroSliderList[index].isSliderDown():
                self.Spectrosliderindex = index
                break

    def SliderReleased(self):
        self.DynamicGraph.SliderChanged(self.sliderindex, self.SliderList[self.sliderindex].value()*(5/99))
                

        

    def SliderPressed(self):    
        for index in range(10):
            if self.SliderList[index].isSliderDown():
                self.sliderindex = index
                break


    def TabChanged(self):
        self.DynamicGraph = self.DynamicGraphList[self.WindowTab.currentIndex()]
        self.Scrollbar = self.ScrollBarList[self.WindowTab.currentIndex()]
        self.SliderList = self.SliderListOfLists[self.WindowTab.currentIndex()]
        self.SpectroSliderList = self.SpectroSliderListOfLists[self.WindowTab.currentIndex()]
        self.SliderResetList = self.SliderResetListOfLists[self.WindowTab.currentIndex()]
        self.ResetSignalMapper = self.SliderMapperResetList[self.WindowTab.currentIndex()]

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
        #TimeOutput,trash, MagnitudeOutput = np.loadtxt(path,unpack=True)
        if self.isFirstTab ==False :
            self.AddTab()
        self.isFirstTab=False
        self.Scrollbar.setValue(99)
        self.DynamicGraph.SetTimeAndMagnitude(Time, Magnitude)
        self.DynamicGraph.SetTimer()
        self.GraphsInPDF+=1
    
    def GetGraphsInPDF(self):
        return self.GraphsInPDF

    def GetTabs(self):
        return self.WindowTab.count()
        
    def AddToPDF(self):
       
        
        self.xDataToPdf.append(self.DynamicGraph.GetxDataPdf())
        self.xDataToPdfOut.append(self.DynamicGraph.GetxDataPdfOutput())
        self.yDataToPdf.append(self.DynamicGraph.GetyDataPdf())
        self.yDataToPdfOut.append(self.DynamicGraph.GetyDataPdfOutput())

        for i in range(len(self.yDataToPdfOut)):
            if i ==len(self.yDataToPdfOut)-1:
                self.fig=plt.figure()
                self.fig,self.axs=plt.subplots(3)
                self.fig.suptitle('Signal '+ str(self.GraphsInPDF))
                self.axs[0].plot( self.xDataToPdf[i],self.yDataToPdf[i] , '#9e4bae')
                self.axs[0].grid(color = "#dccbcf", linewidth = 2)
                self.axs[1].plot( self.xDataToPdfOut[i],self.yDataToPdfOut[i], '#9e4bae')
                self.axs[1].grid(color = "#dccbcf", linewidth = 2)
                self.axs[2].specgram(self.DynamicGraph.GetSpectroDataPdf(), Fs=1, cmap=self.DynamicGraph.GetspectroColor(),vmin = self.DynamicGraph.GetMinIntensity(), vmax = self.DynamicGraph.GetMaxIntensity())
                self.GraphCollection.append(self.fig)


    


        
        
    def CreatePDF(self):
        pdf= matplotlib.backends.backend_pdf.PdfPages("Output.pdf")
        self.AddToPDF()
        for index in range(self.GraphsInPDF):
        
            pdf.savefig(self.GraphCollection[index])
            

        pdf.close()

    
        

    def playAudio(self):
        self.DynamicGraph.PlayAudioSignal()
