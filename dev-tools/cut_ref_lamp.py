from astropy.io import fits

with fits.open("/Users/william/workspace/goodman/goodman/data/lamps/goodman_comp_600Blue_CuHeAr_alt.fits", mode="update") as lamp:
    for r in [range(1,8), range(83,140)]:
        for i in r:
            lamp[0].header["GSP_A%03i" % i] = 0

    # lamp[0].data[0:int(lamp[0].header["GSP_P%03i" % 1])] = 0
    # lamp[0].data[int(lamp[0].header["GSP_P%03i" % 139]):] = 0
    lamp[0].data[0:500] = 0
    lamp[0].data[2500:] = 0

lamp.close()
