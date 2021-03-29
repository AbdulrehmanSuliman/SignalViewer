
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
from PyQt5.QtWidgets import QInputDialog, QFileDialog

import numpy as np
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

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

        if self.IsStop :
            self.CountOut += 1
            if self.CountOut - self.CountIn >= self.CountRange :
                self.CountIn += 1
                
        self.draw()

    def SetZoomFactor(self,zoomed):
        if zoomed:
            self.ZoomFactor=self.ZoomFactor*0.5
"""            self.CountOut = math.ceil(0.9* self.CountRange)"""
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
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('File', self)
        self.file_menu.addAction('Browse File', self.SelectFile, QtCore.Qt.CTRL + QtCore.Qt.Key_B)
        self.file_menu.addAction('Add To PDF', self.AddToPDF, QtCore.Qt.CTRL + QtCore.Qt.Key_D)
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

        FileName = ""
        i=0
        while path[i] != "." or path[i+1] != "t" or path[i+2] != "x" or path[i+3] != "t":
            if path[i] == '/':
                FileName =""
            else:
                FileName = FileName + path[i]
            i=i+1

        Time, Araf, Magnitude = np.loadtxt(path,unpack=True)

        self.DynamicGraph.SetTimeAndMagnitude(Time, Magnitude)
        self.DynamicGraph.SetTimer()


    def AddToPDF(self):
        print("afeverd")


qApp = QtWidgets.QApplication(sys.argv)
aw = ApplicationWindow()
#
# 
# aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
