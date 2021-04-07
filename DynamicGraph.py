import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets
from math import ceil

class MyMplCanvas(FigureCanvas):

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

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.Time = []
        self.Magnitude = []
        self.CountOut = 0
        self.CountIn = 0
        self.IsStop=True
        self.ZoomFactor = 0.05
        self.IsZoomed=False
        self.CountRange = 200
        self.scrollDisplacement=0
        self.scrollBarValue=99

    def SetIsStop(self):
        if self.IsStop:   
            self.IsStop=False
        else:
            self.IsStop=True

    def PauseSignal(self):
        self.IsStop = False

    def StartSignal(self):
        self.IsStop = True 

    def SetScrollDisplacement(self,movedValue):

        self.scrollDisplacement+=movedValue

    def SetTimer(self):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(100)

    def SetTimeAndMagnitude(self, time, magnitude):
        self.CountOut = 0
        self.CountIn = 0
        self.scrollDisplacement=0
        self.IsStop=True
        self.ZoomFactor = 0.05
        self.IsZoomed=False
        self.CountRange = 200
        self.Time = time
        self.Magnitude = magnitude
        #print(self.Time)

    def update_figure(self):
        self.axes.cla()
        self.Scrolling(self.CountOut+self.scrollDisplacement)
        print(self.scrollDisplacement)
        if self.IsStop:
            self.CountOut += 1
            if self.CountOut - self.CountIn >= self.CountRange :
                self.CountIn += 1
        if self.CountIn+self.scrollDisplacement>= 0 and self.CountIn+self.scrollDisplacement <= self.CountOut:
            self.axes.plot(self.Time[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], self.Magnitude[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], '#9e4bae')
            self.axes.grid(color = "#dccbcf", linewidth = 2)
            
        # else:
        #     if self.scrollDisplacement>0:
        #         self.scrollDisplacement-=50
        #     if self.scrollDisplacement<0:
        #         self.scrollDisplacement+=50
        #     self.axes.plot(self.Time[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], self.Magnitude[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], '#9e4bae')
        #     self.axes.grid(color = "#dccbcf", linewidth = 2)
        #     #self.axes.plot(self.Time[self.CountIn:self.CountOut], self.Magnitude[self.CountIn:self.CountOut], 'r')
        
        self.Spectro.cla()
        #self.Spectro.specgram(self.Magnitude[self.CountIn+self.scrollDisplacement:self.CountOut+self.scrollDisplacement], Fs=100)
        
        self.draw()

    def SetZoomFactor(self,zoomed):
        if zoomed:
            self.CountIn = self.CountIn + ceil( 0.5*(self.CountOut - self.CountIn) )
            self.CountRange = self.CountOut - self.CountIn
            self.IsZoomed=True
        else:
            self.CountIn = self.CountIn - 50
            self.CountRange = self.CountOut - self.CountIn
            if (self.CountIn<0):
                self.CountIn = 0 
            self.IsZoomed=False

    def ScrollUpdator(self, percentage ):
        self.scrollBarValue=percentage
        # newDisplacement= self.CountOut+self.scrollDisplacement - ceil((self.scrollBarValue * self.CountOut)/90)
        # if newDisplacement >= 0:
        #     self.scrollDisplacement -= newDisplacement
        # else:
        #     self.scrollDisplacement += newDisplacement
        print(self.scrollBarValue)

    def Scrolling(self , lastIndexNow):
        newDisplacement=0
        if self.CountOut >=200:
            newDisplacement= self.CountOut-200 - ceil((self.scrollBarValue * (self.CountOut-200))/99)
            print(newDisplacement)
        # newDisplacement= lastIndexNow - ceil((self.scrollBarValue * self.CountOut)/99)
        
        print("ola")
        if self.CountIn-newDisplacement >= 0:
            print("loko")
            self.scrollDisplacement = -newDisplacement

        # if newDisplacement >= 0:
        #     self.scrollDisplacement -= newDisplacement
        # else:
        #     self.scrollDisplacement += newDisplacement
            