import matplotlib.pyplot as plt
from astropy.io import fits

from goodman.spectroscopy.wsbuilder import ReadWavelengthSolution

reference_file = "/Users/william/workspace/goodman/goodman/data/ref_comp/goodman_comp_600-old_BLUE_CuHeAr.fits"

ref_data = fits.getdata(reference_file)
ref_header = fits.getheader(reference_file)
fits_ws_reader = ReadWavelengthSolution(ref_header, ref_data)
reference_solution = fits_ws_reader()

plt.plot(reference_solution[0], reference_solution[1], label="Reference")