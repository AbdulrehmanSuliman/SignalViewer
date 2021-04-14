import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages 
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets
from math import ceil
from scipy.fftpack import fft
from scipy.fftpack import rfft, rfftfreq ,irfft
import numpy as np


class MyMplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.Input = fig.add_subplot(311)
        self.Output = fig.add_subplot(312)
        self.Spectro = fig.add_subplot(313)

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
        self.TimeOutput = []
        self.Magnitude = []
        self.MagnitudeOutput = []
        self.CountOut = 0
        self.CountIn = 0
        self.IsStop=True
        self.ZoomFactor = 0.05
        self.IsZoomed=False
        self.CountRange = 200
        self.scrollDisplacement=0
        self.scrollBarValue=99
        self.pageRight= False
        self.pageLeft= False
        self.movePages=0
        self.val=[0]*10
        #self.val0=self.val1=self.val2=self.val3=self.val4=self.val5=self.val6=self.val7=self.val8=self.val9=0
        self.FTOfMagnitude=np.array([])
        
        

    def SetIsStop(self):
        if self.IsStop:   
            self.IsStop=False
        else:
            self.IsStop=True

    def PauseSignal(self):
        self.IsStop = False

    def StartSignal(self):
        self.IsStop = True 

    def SetMovePages(self):
        if self.pageLeft :
            self.movePages-=200
            self.pageLeft =False
        if self.pageRight:
            self.movePages+=200
            self.pageRight=False



    def setpageRight(self):
        self.pageRight=True

    def setpageLeft(self):
        self.pageLeft=True
    
    def SetTimer(self):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1)

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
        self.TimeOutput = time
        self.FTOfMagnitude = rfft(self.Magnitude)
        self.MagnitudeOutput = magnitude
        self.MaxMagnitude = max(self.Magnitude)
        self.MinMagnitude = min(self.Magnitude)
        self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
        self.MinMagnitudeOutput = min(self.MagnitudeOutput)
        

        

    def update_figure(self):
        self.Input.cla()
        self.Output.cla()
        self.Scrolling(self.CountOut+self.scrollDisplacement)
        #print(self.scrollDisplacement)
        self.SetMovePages()
        if self.IsStop:
            self.CountOut += 1
            if self.CountOut - self.CountIn >= self.CountRange :
                self.CountIn += 1
            else:
                self.Input.set_xlim(0, 200)
                self.Output.set_xlim(0, 200)

        self.Input.set_ylim(self.MinMagnitude, self.MaxMagnitude)
        self.Output.set_ylim(self.MinMagnitudeOutput, self.MaxMagnitudeOutput)
        if self.CountIn+self.scrollDisplacement+self.movePages>= 0 and self.CountIn+self.scrollDisplacement +self.movePages<= self.CountOut:
            self.Input.plot(self.Time[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], self.Magnitude[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], '#9e4bae')
            self.Input.grid(color = "#dccbcf", linewidth = 2)
            self.Output.plot(self.TimeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], self.MagnitudeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], '#9e4bae')
            self.Output.grid(color = "#dccbcf", linewidth = 2)
            
            
        else:
            if self.movePages>0:
                self.movePages-=200
            if self.movePages<0:
                self.movePages+=200
            self.Input.plot(self.Time[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], self.Magnitude[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], '#9e4bae')
            self.Input.grid(color = "#dccbcf", linewidth = 2)
            self.Output.plot(self.TimeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], self.MagnitudeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], '#9e4bae')
            self.Output.grid(color = "#dccbcf", linewidth = 2)
            
        
        self.Spectro.cla()         
        # #self.Spectro.specgram(self.Magnitude[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], Fs=100)
        self.Spectro.specgram(self.MagnitudeOutput, Fs=1)

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
    
    def SetSliderValueUp(self,index,value):
        self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))] *ceil((value))

    #    #elf.MagnitudeOutput[ceil((index/10)*len(self.MagnitudeOutput)):ceil(((index+1)/10)*len(self.MagnitudeOutput))]=self.MagnitudeOutput[ceil((index/10)*len(self.MagnitudeOutput)):ceil(((index+1)/10)*len(self.MagnitudeOutput))] *ceil((value))
    def SetSliderValueDown(self,index,value):
        self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))] /(ceil((self.val[index]-value+1)))

    def SliderChanged(self, index, value):
        for i in range(10):
            if i==index:
                if value>self.val[i]:
                    #print("in")
                # print(self.MagnitudeOutput[10])
                    self.SetSliderValueUp(index,value)
                    #print(self.MagnitudeOutput[10])
                    self.val[i]=value
                   # print(self.val0)
                elif value<self.val[i] and value!=0:
                    # print(self.MagnitudeOutput[10])
                    self.SetSliderValueDown(index,value)
                    # print(self.MagnitudeOutput[10])
                    self.val[i]=value
        


        self.MagnitudeOutput = irfft(self.FTOfMagnitude)
        self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
        self.MinMagnitudeOutput = min(self.MagnitudeOutput)


    # def SliderChanged(self, index, value):
        
    #     #print("Index: {}, Value: {}".format(index, value))
    #     if index==0:
    #         if value>self.val0:
    #             #print("in")
    #            # print(self.MagnitudeOutput[10])
    #             self.SetSliderValueUp(index,value)
    #             #print(self.MagnitudeOutput[10])
    #             self.val0=value
    #             print(self.val0)
    #         elif value<self.val0 and value!=0:
    #             print(self.MagnitudeOutput[10])
    #             self.SetSliderValueDown(index,value)
    #             print(self.MagnitudeOutput[10])
    #             self.val0=value
    #             #val0=value
    #     elif index==1:
    #         if value>self.val1:
    #             self.SetSliderValueUp(index,value)
    #             self.val1=value
    #         elif value<self.val1 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val1=value

    #     elif index==2:
    #         if value>self.val2:
    #             self.SetSliderValueUp(index,value)
    #             self.val2=value
    #         elif value<self.val2 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val2=value

    #     elif index==3:
    #         if value>self.val3:
    #             self.SetSliderValueUp(index,value)
    #             self.val3=value
    #         elif value<self.val3 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val3=value

    #     elif index==4:
    #         if value>self.val4:
    #             self.SetSliderValueUp(index,value)
    #             self.val4=value
    #         elif value<self.val4 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val4=value

    #     elif index==5:
    #         if value>self.val5:
    #             self.SetSliderValueUp(index,value)
    #             self.val5=value
    #         elif value<self.val5 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val5=value

    #     elif index==6:
    #         if value>self.val6:
    #             self.SetSliderValueUp(index,value)
    #             self.val6=value
    #         elif value<self.val6 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val6=value

    #     elif index==7:
    #         if value>self.val7:
    #             self.SetSliderValueUp(index,value)
    #             self.val7=value
    #         elif value<self.val7 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val7=value

    #     elif index==8:
    #         if value>self.val8:
    #             self.SetSliderValueUp(index,value)
    #             self.val8=value
    #         elif value<self.val8 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val8=value

    #     elif index==9:
    #         if value>self.val9:
    #             self.SetSliderValueUp(index,value)
    #             self.val9=value
    #         elif value<self.val9 and value!=0:
    #             self.SetSliderValueDown(index,value)
    #             self.val9=value
    #     self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
    #     self.MinMagnitudeOutput = min(self.MagnitudeOutput)


        






    def ScrollUpdator(self, percentage ):
        self.scrollBarValue=percentage
        #print(self.scrollBarValue)

    def Scrolling(self , lastIndexNow):
        newDisplacement=0
        if self.CountOut >=200:
            newDisplacement= self.CountOut-200 - ceil((self.scrollBarValue * (self.CountOut-200))/99)
            #print(newDisplacement)

        
        if self.CountIn-newDisplacement >= 0:
            self.scrollDisplacement = -newDisplacement
    
    def AddToPDF(self):
        self.fig=plt.figure()
        self.fig,self.axs=plt.subplots(3)
        self.axs[0].plot(self.Time[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], self.Magnitude[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], '#9e4bae')
        self.axs[0].grid(color = "#dccbcf", linewidth = 2)
        self.axs[1].plot(self.TimeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], self.MagnitudeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages], '#9e4bae')
        self.axs[1].grid(color = "#dccbcf", linewidth = 2)
        self.axs[2].specgram(self.MagnitudeOutput, Fs=1)
        return self.fig
    
    def CreatePDF(self):
        pdf= matplotlib.backends.backend_pdf.PdfPages("Output.pdf")
        graph1=self.AddToPDF()
        pdf.savefig(graph1)
        pdf.close()




        

            
