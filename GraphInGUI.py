
# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QApplication

from PyQt5.QtGui import *
from PIL import Image
import numpy as np
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math
from reportlab.pdfgen import canvas 

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(211)
        self.Spectro = fig.add_subplot(212)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.Time = []
        self.Magnitude = []
        self.CountOut = 0
        self.CountIn = 0
        self.IsStop=True
        self.ZoomFactor = 1
        self.IsZoomed=False
        self.CountRange = 200
        self.scrollDisplacement=0

    def SetIsStop(self):
        if self.IsStop:   
            self.IsStop=False
        else:
            self.IsStop=True

    def SetScrollDisplacement(self,movedValue):
        self.scrollDisplacement+=movedValue


    def SetTimer(self):
        self.CountIn = 0
        self.CountOut = 0
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1)

    def SetTimeAndMagnitude(self, time, magnitude):
        self.Time = time
        self.Magnitude = magnitude
        print(self.Time)

    def update_figure(self):
        self.axes.cla()
        self.axes.margins(x=self.ZoomFactor , y=self.ZoomFactor)
        self.axes.plot(self.Time[self.CountIn:self.CountOut], self.Magnitude[self.CountIn:self.CountOut], 'r')
        if self.IsStop:
            self.CountOut += 1
            if self.CountOut - self.CountIn >= self.CountRange :
                self.CountIn += 1

        if self.CountIn+self.scrollDisplacement>= 0:
            self.axes.plot(self.Time[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], self.Magnitude[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], 'r')
        else:
            self.axes.plot(self.Time[self.CountIn:self.CountOut], self.Magnitude[self.CountIn:self.CountOut], 'r')
        
        self.Spectro.cla()
        self.Spectro.specgram(self.Magnitude[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], Fs=100)
        
        if self.IsStop :
            self.CountOut += 1
            if self.CountOut - self.CountIn >= self.CountRange :
                self.CountIn += 1
                
        self.draw()

    def SetZoomFactor(self,zoomed):
        if zoomed:
            self.ZoomFactor=self.ZoomFactor*0.5
# """            self.CountOut = math.ceil(0.9* self.CountRange)"""
            self.IsZoomed=True
        else:
            self.ZoomFactor=self.ZoomFactor+0.5*(1-self.ZoomFactor)
            """self.CountOut = math.ceil(2*self.CountRange)
            self.CountIn = self.CountIn - (self.CountRange - (self.CountOut - self.CountIn))
            if (self.CountIn<0):
                self.CountIn = 0"""
            self.IsZoomed=False
            

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.fname=""
        self.ImageList=[]
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('File', self)
        self.file_menu.addAction('Browse File', self.SelectFile, QtCore.Qt.CTRL + QtCore.Qt.Key_B)
        self.file_menu.addAction('Add To PDF', self.AddToPDF, QtCore.Qt.CTRL + QtCore.Qt.Key_D)
        self.file_menu.addAction('Create PDF', self.CreatePDF, QtCore.Qt.CTRL + QtCore.Qt.Key_P)
        self.file_menu.addAction('Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.tools_menu = QtWidgets.QMenu('Tools', self)
        self.tools_menu.addAction('Stop signal', self.stopSignal,QtCore.Qt.Key_Space)
        self.tools_menu.addAction('Zoom in', self.ZoomIn,QtCore.Qt.Key_Z)
        self.tools_menu.addAction('Zoom out', self.ZoomOut,QtCore.Qt.Key_O)
        
        #self.tools_menu.addAction('continue signal', self.ConSignal, QtCore.Qt.CTRL + QtCore.Qt.Key_C)
        self.menuBar().addMenu(self.tools_menu)

        self.scroll_menu = QtWidgets.QMenu('Scroll', self)
        self.scroll_menu.addAction('Move Right', self.MoveRight, QtCore.Qt.CTRL + QtCore.Qt.Key_R)
        self.scroll_menu.addAction('Move Left', self.MoveLeft, QtCore.Qt.CTRL + QtCore.Qt.Key_L)
        self.menuBar().addMenu(self.scroll_menu)

        self.help_menu = QtWidgets.QMenu('Help', self)
        #self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&About', self.about)
        

        

        self.main_widget = QtWidgets.QWidget(self)

        Layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.DynamicGraph = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        Layout.addWidget(self.DynamicGraph)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

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


    def about(self):
        QtWidgets.QMessageBox.about(self, "About", """sifjsjm""")
    
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
        self.ImageList.append(im1)
        
        
        
        
        
        
        
        
        
        
            
        
    
    def CreatePDF(self):
        fileName = 'Report.pdf'
        documentTitle = 'Report'
        pdf = canvas.Canvas(fileName)
        pdf.setTitle(documentTitle)
        pdfmetrics.registerFont( TTFont('abc', 'SakBunderan.ttf') )
        pdf.setFont('abc', 36)
        pdf.drawCentredString(300, 770, 'Report')   #title



        # pdf.drawString(100,810, 'x100')
        # pdf.drawString(200,810, 'x200')
        # pdf.drawString(300,810, 'x300')
        # pdf.drawString(400,810, 'x400')
        # pdf.drawString(500,810, 'x500')

        # pdf.drawString(10,100, 'y100')
        # pdf.drawString(10,200, 'y200')
        # pdf.drawString(10,300, 'y300')
        # pdf.drawString(10,400, 'y400')
        # pdf.drawString(10,500, 'y500')
        # pdf.drawString(10,600, 'y600')
        # pdf.drawString(10,700, 'y700')
        # pdf.drawString(10,800, 'y800')
        #EEEEEEEEEECCCCCCCCCCCCGGGGGGGGGG
        pdf.setFillColorRGB(0, 0, 0)    #subtitle
        pdf.setFont("Courier-Bold", 14)
        pdf.drawString(70,720, "ECG")
        pdf.drawString(350,670, "Notes:-")
        # pdf.line(70, 715, 140, 715)
        pdf.drawInlineImage(self.ImageList[0],70, 490)
        #EEEEEEEEEEEEEEEEEEGGGGGGGGGGGGGGGG
        pdf.setFillColorRGB(0, 0, 0)    #subtitle
        pdf.setFont("Courier-Bold", 14)
        pdf.drawString(350,460, "EEG")
        pdf.drawString(100,400, "Notes:-")
        # pdf.line(300, 455, 300, 455)
        pdf.drawInlineImage(self.ImageList[1],300, 220)
        #EEEEEEEEEEEEMMMMMMMMMMMMMMGGGGGGGGG
        pdf.setFillColorRGB(0, 0, 0)    #subtitle
        pdf.setFont("Courier-Bold", 14)
        pdf.drawString(70,230, "EMG")
        pdf.drawString(350,150, "Notes:-")
        # pdf.line(70, 195, 140, 195)
        pdf.drawInlineImage(self.ImageList[2],70, 0)



        pdf.save()



        



qApp = QtWidgets.QApplication(sys.argv)
aw = ApplicationWindow()
#
# 
# aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
