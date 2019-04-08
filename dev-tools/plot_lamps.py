import os

import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
from scipy.signal import correlate

reference_file = "/Users/william/workspace/goodman/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr.fits"
ref_data, ref_header = fits.getdata(reference_file, header=True)
ref_scale = 100 #3.67

ref_data *= ref_scale

# workdir = "/Users/william/data/SOAR/2017B/Noite4/2017-10-27/"
workdir = "/Users/william/Downloads/li/li2"
for fname in os.listdir(workdir):
    if "CuHeAr" in fname:
        print("@@@>", fname)
        plt.clf()
        plt.plot(ref_data, label="ref", color='blue')

        data, header = fits.getdata("%s/%s" % (workdir, fname), header=True)
        lag = np.argmax(correlate(ref_data, data))
        # signal = np.roll(aux*100, shift=int(np.ceil(lag)))
        signal = np.roll(data, shift=int(np.ceil(lag)))
        plt.plot(signal, label='comp, corellated', alpha=0.5, color='red')

        plt.legend()
        plt.draw()
        input("next...")

