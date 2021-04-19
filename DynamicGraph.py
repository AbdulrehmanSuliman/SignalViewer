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
from scipy.io.wavfile import write
import simpleaudio as sa

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
        self.MaxIntensity = 0
        self.MinIntensity = 0
        self.pageRight= False
        self.pageLeft= False
        self.movePages=0
        self.val=[1]*10
        self.GraphNumber=0
        self.SpectroColor = 'viridis'
        self.FTOfMagnitude=np.array([])
        # validation signal
        self.SAMPLE_RATE = 44100  # Hertz 

          
               
    def GetspectroColor(self):
        return self.SpectroColor             


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
        self.Spectro.cla()         
        self.Spectro.specgram(self.MagnitudeOutput, Fs=self.SamplingFreq, cmap=self.SpectroColor)
        self.Spectro.set_ylim(self.freqmin/4000,self.freqmax/4000)    

        # x1,x2,y1,y2 = self.Spectro.axis()
        # self.YMax = y2
        # self.MinIntensity = 0
        # self.MaxIntensity = y2 

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
        self.FTOfMagnitude =np.abs( rfft(self.Magnitude))
        self.MagnitudeOutput = magnitude
        self.MaxMagnitude = max(self.Magnitude)
        self.MinMagnitude = min(self.Magnitude)
        self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
        self.MinMagnitudeOutput = min(self.MagnitudeOutput)
        # min max spectro
        self.freqmin = 0
        self.freqmax = len(self.FTOfMagnitude)-1 
        self.SamplingFreq = len(self.FTOfMagnitude)/2000

        
        
            

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

        self.draw()


    def GetxDataPdf(self):
        return self.Time[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages] 
    def GetyDataPdf(self):
        return self.Magnitude[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages]
    def GetxDataPdfOutput(self):
        return self.TimeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages]
    def GetyDataPdfOutput(self):
        return self.MagnitudeOutput[self.CountIn+self.scrollDisplacement+self.movePages:self.CountOut+self.scrollDisplacement+self.movePages]
    def GetSpectroDataPdf(self):
        return self.MagnitudeOutput

    def ChangeSpectroColor(self, index):
        if index == 0:
            self.SpectroColor = 'viridis'
        elif index == 1:
            self.SpectroColor = 'plasma'
        elif index == 2:
            self.SpectroColor = 'inferno'
        elif index == 3:
            self.SpectroColor = 'magma'
        elif index == 4:
            self.SpectroColor = 'cividis'
        self.Spectro.cla()         
        self.Spectro.specgram(self.MagnitudeOutput, Fs=self.SamplingFreq, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity) 
        self.Spectro.set_ylim(self.freqmin/4000,self.freqmax/4000)    
   
        #self.Spectro.axis([x1,x2,self.MinIntensity,self.MaxIntensity])
        



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
    
  
    def SliderChanged(self, index, value):
        if len(self.Magnitude) > 0:
            for i in range(10):
                if i==index:
                    if self.val[i] == 0:
                        self.FTOfMagnitude =np.abs( rfft(self.Magnitude))

                        for counter in range(10):
                            if counter == i :
                                self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]  * value
                            else :
                                self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]  * self.val[counter]
                                
                    else :                        
                        self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))] / self.val[i] * value
   
                    self.val[i]=value
            self.MagnitudeOutput =-irfft(self.FTOfMagnitude[self.freqmin:self.freqmax])
            self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
            self.MinMagnitudeOutput = min(self.MagnitudeOutput)
            self.Spectro.cla()         
            self.Spectro.specgram(self.MagnitudeOutput, Fs=self.SamplingFreq, cmap=self.SpectroColor)
            self.Spectro.set_ylim(self.freqmin/4000,self.freqmax/4000)    
    
            #self.Spectro.axis([x1,x2,self.MinIntensity,self.MaxIntensity])
        

    def SpectroSliderChanged(self, index, value):
        #x1,x2,y1,y2 = self.Spectro.axis()
        #print(x1,x2)
        # st=0
        # end=len(self.FTOfMagnitude)/4000
        #print(len(self.FTOfMagnitude))
        if index==0 :
            #self.MinIntensity = (((self.YMax/2)-0.01)/99)*value
            self.MinIntensity = -2*value 
            #self.MaxIntensity = int((((len(self.MagnitudeOutput)/2)-1)/99)*value + (len(self.MagnitudeOutput)/2))
            print(self.MinIntensity)
            self.freqmin=ceil((len(self.FTOfMagnitude)/2*value)/99)
            
        if index==1 :
            #self.MaxIntensity = (((self.YMax/2)-0.01)/99)*value + self.YMax/2
            self.MaxIntensity = 2*value
            self.freqmax = ceil(((len(self.FTOfMagnitude)/2*value)/99)+len(self.FTOfMagnitude)/2)
        # newFt = self.FTOfMagnitude[self.freqmin:self.freqmax]

        # newmag=-irfft(newFt)
        if(self.MinIntensity<self.MaxIntensity):
            self.Spectro.cla()         
            self.Spectro.specgram(self.MagnitudeOutput, Fs=self.SamplingFreq, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity)
            #print(self.freqmin/2000,self.freqmax/4000)
            #self.Spectro.specgram(self.MagnitudeOutput, Fs=len(self.FTOfMagnitude)/2000, cmap=self.SpectroColor)
            self.Spectro.set_ylim(self.freqmin/4000,self.freqmax/4000)    
            # self.Spectro.set_ylim(1.5,19.7)    
            #self.Spectro.axis([x1,x2,self.MinIntensity,self.MaxIntensity])
        else:
            pass
    
    def GetMinIntensity(self):
        return self.MinIntensity
    
    def GetMaxIntensity(self):
        return self.MaxIntensity


    def PlayAudioSignal(self):

        write("mysinewave.wav", self.SAMPLE_RATE, np.int16((self.MagnitudeOutput / self.MagnitudeOutput.max()) * 5000))
        wave_obj = sa.WaveObject.from_wave_file("mysinewave.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def ScrollUpdator(self, percentage ):
        self.scrollBarValue=percentage

    def Scrolling(self , lastIndexNow):
        newDisplacement=0
        if self.CountOut >=200:
            newDisplacement= self.CountOut-200 - ceil((self.scrollBarValue * (self.CountOut-200))/99)

        
        if self.CountIn-newDisplacement >= 0:
            self.scrollDisplacement = -newDisplacement
    
    
   



        

            
