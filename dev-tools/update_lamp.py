import os
import pickle
from shutil import copyfile

from astropy.io import fits
import numpy as np

from pipeline.tools.reference_lamp_factory.wcs_model_calculator import GSPWcsCalculator

semester = "2017B"

# Get correspondence
correspondence = np.array(pickle.load(open("correspondece.pkl", "rb")))

# write new wl and angstroms to fits header
copyfile("/Users/william/Downloads/li/ecfzsto_0117_CuHeAr.fits", "tmp.fits")
f = fits.open("tmp.fits", mode="update")

# Sort correspondence
correspondence = correspondence[np.argsort(correspondence[:,1])]
for i_c, c in enumerate(correspondence):
    f[0].header.update({"GSP_A%03d" % (i_c+1): c[0]})
    f[0].header.update({"GSP_P%03d" % (i_c+1): c[1]})
f.close()


g = GSPWcsCalculator()
# g("/Users/william/workspace/goodman/goodman/data/lamps/goodman_comp_600Blue_CuHeAr_alt.fits", save=True)
g("tmp.fits", save=True)

if not os.path.exists("goodman_comp_600Blue_CuHeAr_%s.fits" % semester):
    copyfile(g.ccd.header['GSP_FNAM'], "goodman_comp_600Blue_CuHeAr_%s.fits" % semester)
    f = fits.open("goodman_comp_600Blue_CuHeAr_%s.fits" % semester, mode="update")
    f[0].header.update({"GSP_FNAM": "goodman_comp_600Blue_CuHeAr_%s.fits" % semester})
    f.close()
else:
    print("goodman_comp_600Blue_CuHeAr_%s.fits exists. delete it first!" % semester)
