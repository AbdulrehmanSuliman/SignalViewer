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
        self.MinIntensity = -100
        self.pageRight= False
        self.pageLeft= False
        self.movePages=0
        self.val=[1]*10
        self.GraphNumber=0
        self.SpectroColor = 'viridis'
        #self.val0=self.val1=self.val2=self.val3=self.val4=self.val5=self.val6=self.val7=self.val8=self.val9=0
        self.FTOfMagnitude=np.array([])
        # validation signal
        self.SAMPLE_RATE = 44100  # Hertz    
        # self.DURATION = 10  # Seconds
        # self.validation_signal=[]
        # #self.generate_sine_wave(1,1,2)
        # self.generate_Validation_Signal()
                
    def GetspectroColor(self):
        return self.SpectroColor             

    # def generate_sine_wave(self,freq, sample_rate, duration):
    
    #     x = np.linspace(0, duration, sample_rate * duration, endpoint=False)
    #     frequencies = x * freq
    #     # 2pi because np.sin takes radians
    #     y = np.sin((2 * np.pi) * frequencies)
    #     return y

    # def generate_Validation_Signal(self):
    #     listOfFrequencies=[200,500,1000,1,5000 , 700 ,10000 , 1500 , 100]
    #     mixed_signl=self.generate_sine_wave(10,self.SAMPLE_RATE,self.DURATION)
    #     for freq in listOfFrequencies:
    #         mixed_signl += self.generate_sine_wave(freq,self.SAMPLE_RATE,self.DURATION)

    #     self.validation_signal = np.int16((mixed_signl / mixed_signl.max()) * 5000)
    #     print(self.validation_signal)

    

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
        self.Spectro.specgram(self.MagnitudeOutput, Fs=1, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity)

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
        

        
    # def SetTimeAndMagnitude_Validation(self):
    #     self.CountOut = 0
    #     self.CountIn = 0
    #     self.scrollDisplacement=0
    #     self.IsStop=True
    #     self.ZoomFactor = 0.05
    #     self.IsZoomed=False
    #     self.CountRange = 200
    #     self.Time = np.linspace(0, self.DURATION, self.SAMPLE_RATE * self.DURATION, endpoint=False)
    #     self.Magnitude = self.validation_signal    
    #     self.TimeOutput = self.Time
    #     self.FTOfMagnitude = rfft(self.Magnitude)
    #     self.MagnitudeOutput = self.Magnitude
    #     self.MaxMagnitude = max(self.Magnitude)
    #     self.MinMagnitude = min(self.Magnitude)
    #     self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
    #     self.MinMagnitudeOutput = min(self.MagnitudeOutput)
        
        
        

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
        
       




        # self.Spectro.cla()         
        # self.Spectro.specgram(self.MagnitudeOutput, Fs=1, cmap=self.SpectroColor)

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
        self.Spectro.specgram(self.MagnitudeOutput, Fs=1, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity)
        



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
    
    # def SetSliderValueUp(self,index,value):
    #     self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))] *ceil((value))

    # def SetSliderValueDown(self,index,value):
    #     self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))]=self.FTOfMagnitude[ceil((index/10)*len(self.FTOfMagnitude)):ceil(((index+1)/10)*len(self.FTOfMagnitude))] /(ceil((self.val[index]-value+1)))

    # def SliderChanged(self, index, value):
    #     if len(self.Magnitude) > 0:
    #         for i in range(10):
    #             if i==index:
    #                 if value>self.val[i]:
    #                     self.SetSliderValueUp(index,value)
    #                     self.val[i]=value


    #                 elif value<self.val[i] and value!=0:
    #                     self.SetSliderValueDown(index,value)
    #                     self.val[i]=value
    #                 elif value == 0:
    #                     self.SetSliderValueUp(index,value)
    #                     self.val[i]=value

    #         self.MagnitudeOutput = irfft(self.FTOfMagnitude)
    #         self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
    #         self.MinMagnitudeOutput = min(self.MagnitudeOutput)
    #         self.Spectro.cla()         
    #         self.Spectro.specgram(self.MagnitudeOutput, Fs=1, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity)

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
                    print(i,self.val[i], value)
            self.MagnitudeOutput =-irfft(self.FTOfMagnitude)
            self.MaxMagnitudeOutput = max(self.MagnitudeOutput)
            self.MinMagnitudeOutput = min(self.MagnitudeOutput)
            self.Spectro.cla()         
            self.Spectro.specgram(self.MagnitudeOutput, Fs=1, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity)
        

    def SpectroSliderChanged(self, index, value):
        if index==0:
            self.MinIntensity = -value *2
        if index==1:
            self.MaxIntensity = value *2
        self.Spectro.cla()         
        self.Spectro.specgram(self.MagnitudeOutput, Fs=1, cmap=self.SpectroColor, vmin = self.MinIntensity, vmax = self.MaxIntensity)
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
        #print(self.scrollBarValue)

    def Scrolling(self , lastIndexNow):
        newDisplacement=0
        if self.CountOut >=200:
            newDisplacement= self.CountOut-200 - ceil((self.scrollBarValue * (self.CountOut-200))/99)
            #print(newDisplacement)

        
        if self.CountIn-newDisplacement >= 0:
            self.scrollDisplacement = -newDisplacement
    
    
   



        

            
