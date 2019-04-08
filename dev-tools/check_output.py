import os

import numpy as np

import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.modeling.polynomial import Chebyshev1D

comp_data, header = fits.getdata(
    "/Users/william/workspace/goodman/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr.fits", header=True)

wl_model = Chebyshev1D(degree=header["GSP_ORDR"])
for i in range(header['GSP_ORDR'] + 1):
    wl_model.__getattr__('c{:d}'.format(i)).value = header['GSP_C{:03d}'.format(i)]
    wl_comp = wl_model(range(header['GSP_NPIX']))

for filename in os.listdir("/Users/william/Downloads/raw_data/2016-03-07/proccessed/"):
    # filename = "/Users/william/Downloads/raw_data/2016-03-07/proccessed/wecfzsto_0140.SO2016A-006_0307.fits"
    if "wecfzsto" in filename:
        filename = "/Users/william/Downloads/raw_data/2016-03-07/proccessed/" + filename

        data, header = fits.getdata(filename, header=True)

        wl_model = Chebyshev1D(degree=header["GSP_ORDR"])
        for i in range(header['GSP_ORDR'] + 1):
            wl_model.__getattr__('c{:d}'.format(i)).value = header['GSP_C{:03d}'.format(i)]
            wl = wl_model(range(header['GSP_NPIX']))

        print(wl)

        plt.clf()
        plt.plot(wl, data)

        # Plot some guidelines...

        elines = [3968.47, 3933.66]

        ymin, ymax = plt.ylim()
        plt.vlines([elines], ymin, ymax, colors="red")

        # plt.title(filename.split('/')[-1])
        plt.title(header["OBJECT"] + "   RMS: %.2f" % header["GSP_WRMS"])
        plt.xlim(3900, 4000)
        aux = data[np.bitwise_and(wl > 3900, wl < 4000)]
        plt.ylim(aux.min() * .9, aux.max() * 1.1)

        if header["OBSTYPE"] == "COMP":
            plt.plot(wl_comp, comp_data)
            aux = comp_data[np.bitwise_and(wl > 3500, wl < 4500)]
            plt.ylim(aux.min() * .9, aux.max() * 1.1)
            plt.xlim(3500,4500)

        plt.draw()
        plt.show()
        input("next")
