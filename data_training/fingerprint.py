# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 11:57:15 2018

@author: user
"""

import numpy as np
import matplotlib.mlab as mlab
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure,
                                      binary_erosion)
import matplotlib.pyplot as plt
import hashlib
from operator import itemgetter

## Spectrogram #############################################

def Spectrogram(data_mono):
    
    # FFT parameters
    FS = 44100
    WINDOW_SIZE = 4096
    OVERLAP_RATIO = 0.5
    
    spectrogram = mlab.specgram(data_mono,
                                NFFT=WINDOW_SIZE,
                                Fs=FS,
                                window=mlab.window_hanning,
                                noverlap=int(WINDOW_SIZE*OVERLAP_RATIO))[0]
    
    spectrogram = 10 * np.log10(spectrogram)
    spectrogram[spectrogram == -np.inf] = 0
    
    return spectrogram

## Local Maxima ############################################

def Local_Maxima(spectrogram):
    
    # Minimum amplitude in spectrogram to be considered a peak
    AMPLITUDE_MIN = 10
    # Number of cells around a peak to be considered a spectral peak
    NEIGHBORHOOD_SIZE = 20
    
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, NEIGHBORHOOD_SIZE)
    
    spectrogram_filtered = maximum_filter(spectrogram,
                                          footprint=neighborhood)
    
    local_max = (spectrogram_filtered == spectrogram)
    background = (spectrogram == 0)
    eroded_background = binary_erosion(background,
                                       structure=neighborhood,
                                       border_value=1)
    
    peaks = local_max ^ eroded_background
    
    amplitudes = spectrogram[peaks]
    j, i = np.where(peaks)
    amplitudes = amplitudes.flatten()
    
    peaks_info = zip(i, j, amplitudes)
    
    peaks_filtered = [x for x in peaks_info if x[2] > AMPLITUDE_MIN]
    
    time = [x[0] for x in peaks_filtered]
    frequency = [x[1] for x in peaks_filtered]
    
    fig, ax = plt.subplots()
    ax.imshow(spectrogram)
    ax.scatter(time, frequency)
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency')
    ax.set_title("Spectrogram")
    plt.gca().invert_yaxis()
    plt.show()
    
    return zip(frequency, time)

## HASHING #################################################

def Hashing(local_maxima_info):
    
    # Degree to which a fingerprint can be paired with its neighbors
    FAN_VALUE = 15
    # If True, will sort peaks temporally for fingerprinting
    PEAK_SORT = True
    # Thresholds on how close or far fingerprints can be in time
    # to be paired as a fingerprint
    MIN_HASH_TIME_DELTA = 0
    MAX_HASH_TIME_DELTA = 200
    # Number of bits to throw away from the front of the SHA1 hash
    FINGERPRINT_REDUCTION = 20
    
    """
    Hash list structure:
       sha1_hash[0:20]    time_offset
    [(e05b341a9b77a51fd26, 32), ... ]
    """
    
    if PEAK_SORT:
        local_maxima_info.sort(key=itemgetter(1))

    for i in range(len(local_maxima_info)):
        for j in range(1, FAN_VALUE):
            if (i + j) < len(local_maxima_info):
                
                freq1 = local_maxima_info[i][0]
                freq2 = local_maxima_info[i + j][0]
                t1 = local_maxima_info[i][1]
                t2 = local_maxima_info[i + j][1]
                t_delta = t2 - t1

                if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
                    h = hashlib.sha1(
                        "%s|%s|%s" % (str(freq1), str(freq2), str(t_delta))
                        )
                    yield (h.hexdigest()[0:FINGERPRINT_REDUCTION], t1)
    return