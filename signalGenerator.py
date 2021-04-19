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

# Time,trash, Magnitude = np.loadtxt("Signals/Validation.txt",unpack=True)
# print(normalized_tone)
# Magnitude2 = np.int16((Magnitude / Magnitude.max()) * 5000)
# print(Magnitude)
# for i in Magnitude:
#     i=int(i)
# print(Magnitude.astype(int))

# write("mysinewave.wav", SAMPLE_RATE, Magnitude2)
# filename = 'mysinewave.wav'
# wave_obj = sa.WaveObject.from_wave_file("mysinewave.wav")
# play_obj = wave_obj.play()
# play_obj.wait_done()
