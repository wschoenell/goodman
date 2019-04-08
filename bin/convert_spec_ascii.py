import sys

from astropy.io import fits
from astropy.modeling.polynomial import Chebyshev1D

fname = sys.argv[1]

if not "wecfzsto" in fname:
    raise Exception("Unknown file type.")

data, header = fits.getdata(fname, header=True)

output = "### goodman pipeline output ASCCI file ###\n"
output += "# " + repr(header).replace("\n", "\n# ") + "\n"
output += "# wl     flux\n"

wl_model = Chebyshev1D(degree=header["GSP_ORDR"])
for i in range(header['GSP_ORDR'] + 1):
    wl_model.__getattr__('c{:d}'.format(i)).value = header['GSP_C{:03d}'.format(i)]
    wl = wl_model(range(header['GSP_NPIX']))

for i_line in range(len(wl)):
    output += "%.2f %.4f\n" % (wl[i_line], data[i_line])

fout = fname.replace(".fits", ".dat")
with open(fout, 'w') as fp:
    fp.write(output)
