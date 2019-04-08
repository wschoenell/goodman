import pickle
import re

import scipy

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.modeling import models, fitting, Model

from pipeline.tools.reference_lamp_factory.wcs_model_calculator import GSPWcsCalculator


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also: 

    np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y[int(np.ceil(window_len / 2 - 1)):-int(np.ceil(window_len / 2))]


# reference_file = "/Users/william/Downloads/raw_data/2016-03-07/reduced/cfzsto_0147.SO2016A-006_0307.fits"
# reference_file = "/Users/william/Downloads/cfzsto_0083_CuHeAr.fits"
# comp_file = "ecfzsto_1099.SO2016B-104_1026.fits"
comp_file = "/Users/william/Downloads/li/ecfzsto_0117_CuHeAr.fits"
# comp_file = "/Users/william/workspace/goodman/goodman/data/lamps/goodman_comp_600Blue_CuHeAr_alt.fits"

# reference_file = "/Users/william/Downloads/raw_data/2016-03-07/RED/gcfzsto_0152.SO2016A-006_0307.fits"
# reference_file = "/Users/william/workspace/goodman/goodman/data/ref_comp/goodman_comp_600-old_BLUE_CuHeAr.fits"
comp_data, comp_header = fits.getdata(comp_file, header=True)#.sum(axis=0)
comp_data = comp_data[:-1]

# if 'ref_comp' in comp_file:
comp_data /= 10

# comp_data = comp_data[:2500]

# ### OLD CALIBRATION ####
# # reference_file = "/Users/william/Downloads/WS/RED/cfzsto_0047.SO2016A-019_0320.fits"
# reference_file = "/Users/william/workspace/goodman/goodman/data/lamps/linear-raw-1d.fits"
# # comp_data = fits.getdata(reference_file).sum(axis=0) / 1000.
# comp_data = fits.getdata(reference_file) / 100.
# ref_header = fits.getheader(reference_file)

### NEW CALIBRATION ###
reference_file = "/Users/william/workspace/goodman/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr.fits"
ref_data, ref_header = fits.getdata(reference_file, header=True)

# ref_data = smooth(ref_data, 13)

# ref_data *= .10
# ref_data = ref_data[:2500]
model_name = ref_header['GSP_FUNC']
degree = ref_header['GSP_ORDR']

if model_name == 'Chebyshev1D':
    model = models.Chebyshev1D(degree=degree)
    for i in range(ref_header['GSP_ORDR'] + 1):
        model.__getattr__('c{:d}'.format(i)).value = ref_header[
            'GSP_C{:03d}'.format(i)]
    wavelength_and_intensity = [
        model(range(ref_header['GSP_NPIX'])), ref_data]

    ref_data = wavelength_and_intensity[1]


# raw_input("caca")

# x = np.arange(len(ref_data))
#
# data1 = np.array([x, ref_data])
# data2 = np.array([x+10, ref_data])

# reference_file2 = "/Users/william/Downloads/raw_data/2016-03-07/RED/gcfzsto_0141.SO2016A-006_0307.fits"
# comp_data = fits.getdata(reference_file2)

aux = np.zeros_like(ref_data)
aux[:len(comp_data)] = comp_data

x = np.arange(len(ref_data))
plt.close()
plt.figure(figsize=(32, 6))
plt.clf()
plt.plot(x, ref_data, label='reference', color='green')
# plt.plot(x, aux*100, label='observed', color='black')

from scipy.signal import correlate
lag = np.argmax(correlate(ref_data, aux))
# signal = np.roll(aux*100, shift=int(np.ceil(lag)))
signal = np.roll(aux, shift=int(np.ceil(lag)))
plt.plot(x, signal, label='comp, corellated', alpha=0.8, color='red')

boxes = np.linspace(x.min(), x.max(), 11)
ymin, ymax = plt.ylim()
plt.vlines(boxes[:-1], ymin, ymax, colors='blue')
plt.vlines(boxes[1:]+2, ymin, ymax, colors='red')

## detect line peaks ##

#FIXME: hardocded
slit_size = 1.03
serial_binning = 1

angstroms = []
pixels = []

for kw in ref_header.keys():
    if re.match('GSP_P[0-9]', kw):
        plt.gca().axvline(ref_header[kw], color='g', linestyle=':')
        pixels.append(float(ref_header[kw]))
    if re.match('GSP_A[0-9]', kw):
        angstroms.append(ref_header[kw])

angstroms = np.array(angstroms)
pixels = np.array(pixels)

### FROM the pipeline ###
no_nan_lamp_data = np.asarray(np.nan_to_num(signal))

filtered_data = np.where(
    np.abs(no_nan_lamp_data > no_nan_lamp_data.min() +
           0.03 * no_nan_lamp_data.max()),
    no_nan_lamp_data,
    None)

# replace None to zero and convert it to an array
none_to_zero = [0 if it is None else it for it in filtered_data]
filtered_data = np.array(none_to_zero)

new_order = int(round(float(slit_size) / (0.15 * serial_binning)))
peaks = scipy.signal.argrelmax(filtered_data, axis=0, order=new_order)[0]
for line in peaks:
    plt.gca().axvline(line, color='r', linestyle=':')

plt.legend()
plt.show()

lims = None
def on_xlims_change(axes):
    lims = [plt.gca().get_xlim(), plt.gca().get_ylim()]

def on_ylims_change(axes):
    lims = [plt.gca().get_xlim(), plt.gca().get_ylim()]

plt.gca().callbacks.connect('xlim_changed', on_xlims_change)
plt.gca().callbacks.connect('ylim_changed', on_ylims_change)

aux_corresp = [None, None]
correspondence = []

def onkey(event):
    global aux_corresp, aux_pix
    # Grab reference line
    if event.key == 'a':
        i = np.argmin(np.abs(pixels - event.xdata))
        plt.gca().axvline(pixels[i], color='k')
        aux_pix = pixels[i]
        aux_corresp[0] = angstroms[i]
        plt.draw()

        if lims is not None:
            xlim, ylim = lims
            print(xlim, ylim)
            plt.xlim(xlim)
            plt.ylim(ylim)

    # Grab COMP line
    if event.key == 'd':
        i = np.argmin(np.abs(peaks - event.xdata))
        plt.gca().axvline(peaks[i], color='k')
        aux_corresp[1] = peaks[i]
        plt.draw()

        if lims is not None:
            xlim, ylim = lims
            print(xlim, ylim)
            plt.xlim(xlim)
            plt.ylim(ylim)

    # Save
    if event.key == 'v':
        if aux_corresp[0] is None or aux_corresp[1] is None:
            print('Choose two lines.')
        else:
            print("Saved", aux_corresp)
            correspondence.append(np.copy(aux_corresp))
            pickle.dump(correspondence, open('correspondece.pkl', 'wb'))
            plt.gca().axvline(aux_pix, color='g')
            plt.gca().axvline(aux_corresp[1], color='r')
            aux_corresp = [None, None]
    # for line in correspondence:

    # Remove last
    if event.key == 'x':
        print("removed: ", correspondence.pop(-1))


plt.gcf().canvas.mpl_connect('key_press_event', onkey)

save = False
if save:
    with fits.open("/Users/william/workspace/goodman/pipeline/data/ref_comp/goodman_comp_600Blue_CuHeAr_alt.fits", mode="update") as lamp:
        lamp[0].data = np.copy(ref_data)

    lamp.close()

# lamp = fits.open("/Users/william/workspace/goodman/goodman/data/lamps/goodman_comp_600Blue_CuHeAr_alt.fits", mode="update")
#
# for kw in ["GSP_FUNC","GSP_NPIX", "GSP_ORDR", "GSP_C000", "GSP_C001", "GSP_C002", "GSP_C003"]:
#     lamp[0].header.pop(kw)
#
# lamp.close()
#
# g = GSPWcsCalculator()
# g("/Users/william/workspace/goodman/goodman/data/lamps/goodman_comp_600Blue_CuHeAr_alt.fits", save=True)

# x = [int(np.argwhere(pixels == a)) for a in np.array(correspondence)[:,0]]
# np.array(angstroms)[x]
