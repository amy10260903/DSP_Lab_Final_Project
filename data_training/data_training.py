# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import wave
import fingerprint as fp
import numpy as np
#import matplotlib.mlab as mlab
#from scipy.ndimage.filters import maximum_filter
#from scipy.ndimage.morphology import (generate_binary_structure,
#                                      iterate_structure,
#                                      binary_erosion)
#import matplotlib.pyplot as plt

Folder = "./data"
SongName = '/五月天-成名在望'

wav = wave.open(Folder+'/wav'+SongName+'.wav', 'rb')
CHANNEL = wav.getnchannels()
FORMAT = wav.getsampwidth()
RATE = wav.getframerate()
data = wav.readframes(-1)

if CHANNEL > 1:
    data_stereo = np.fromstring(data, 'int16')
    data_stereo.shape = -1, 2
    data_stereo = data_stereo.T
    data_mono = (data_stereo[0] + data_stereo[1]) / 2
else:
    data_mono = np.fromstring(data, 'int16')

spectrogram = fp.Spectrogram(data_mono)
local_max_info = fp.Local_Maxima(spectrogram)

############################################################

#time = np.arange(data.shape[1]) / RATE
#
#plt.figure(1)
#plt.plot(time, data[0])
#
#plt.figure(2)
#plt.plot(time, data[1])

#from dejavu import Dejavu
#config = {
#    'database': {
#    'host': '127.0.0.1',
#    'user': 'root',
#    'passwd': 'weiling1121',
#    'db': 'dejavu',
#    }
#}
#djv = Dejavu(config)
#
#djv.fingerprint_directory("music_data", [".mp3"], 3)
#
#print(djv.db.get_num_fingerprints())