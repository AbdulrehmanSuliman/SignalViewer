import numpy as np
from matplotlib import pyplot as plt
from scipy.io.wavfile import write
#from playsound import playsound
import simpleaudio as sa


SAMPLE_RATE = 44100  # Hertz
DURATION = 2  # Seconds

def generate_sine_wave(freq, sample_rate, duration):

    x = np.linspace(0, duration, sample_rate * duration, endpoint=False)

    frequencies = x * freq
    # 2pi because np.sin takes radians
    y = np.sin((2 * np.pi) * frequencies)
    return  y


listOfFrequencies=[600,1000,2400,2800 , 4200 ,4600 , 8000 , 8400 , 18000 ]

mixed_signl=generate_sine_wave(200,SAMPLE_RATE,DURATION)
for freq in listOfFrequencies:
    mixed_signl += generate_sine_wave(freq,SAMPLE_RATE,DURATION)

normalized_tone = np.int16((mixed_signl / mixed_signl.max()) * 5000)

sigfile=open("Signals/Validation.txt","w")
for i in range(len(normalized_tone)):
    sigfile.write(str(i) + "  0  " + str(normalized_tone[i]) + "\n")

sigfile.close()


