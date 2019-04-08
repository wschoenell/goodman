import os
import re
import sys

from astropy.io import fits

obslog_bad = {"2016-03-07": {"0151": "Science (Bad rotation in the last 20 seconds)", },
              "2016-03-08": {"0099": "Acquisition (test to fit the mask)",
                             "0100": "Acquisition (test to fit the mask)",
                             "0101": "Acquisition (test to fit the mask)",
                             # "0102": "Image to test reference star (probable saturated) - valid but low exposure time",
                             "0106": "Acquisition (test to fit the mask)",
                             "0107": "Acquisition (test to fit the mask)",
                             "0108": "Acquisition (test to fit the mask)",
                             "0110": "Acquisition to test shift to recenter slits",
                             "0111": "Acquisition to test shift to recenter slits",
                             "0112": "Acquisition to reload image (due to telescope problem)",
                             "0113": "Acquisition to reload image (due to telescope problem)",
                             "0119": "Acquisition (test to fit the mask)",
                             "0120": "Acquisition (test to fit the mask)",
                             "0121": "Acquisition (test to fit the mask)",
                             "0125": "Acquisition (test to fit the mask)",
                             "0126": "Acquisition (test to fit the mask)- We must back to this object!",
                             "0128": "Acquisition (test to fit the mask)",
                             "0129": "Acquisition (test to fit the mask)",
                             "0134": "Acquisition (test to fit the mask)",
                             "0135": "Acquisition (test to fit the mask)",
                             "0136": "Acquisition (test to fit the mask)",
                             "0137": "Acquisition (test to fit the mask)",
                             "0150": "Set of images to check focus",
                             "0151": "Set of images to check focus",
                             "0152": "Set of images to check focus",
                             "0153": "Set of images to check focus",
                             "0154": "Set of images to check focus",
                             "0155": "Set of images to check focus",
                             "0156": "Set of images to check focus",
                             },
              "2016-03-09": {"0001": "Calibration",
                             "0002": "Calibration",
                             "0003": "Focus",
                             "0004": "Focus",
                             "0005": "Focus",
                             "0006": "Focus",
                             "0007": "Focus",
                             "0008": "Focus",
                             "0009": "Focus",
                             "0010": "Focus",
                             "0121": "Acquisition (test to fit the mask)",
                             "0122": "Acquisition (test to fit the mask)",
                             "0123": "Acquisition (test to fit the mask)",
                             "0124": "Acquisition (test to fit the mask)",
                             ### TODO: Skipped a lot of MOS observations on the log ###
                             # "0183": "Science - Refazer",
                             },
              "2016-03-10": {"0001": "test",
                             "0002": "focus",
                             "0003": "focus",
                             "0004": "focus",
                             "0005": "focus",
                             "0006": "focus",
                             "0007": "focus",
                             "0008": "focus",
                             "0009": "focus",
                             "0010": "focus",
                             "0011": "focus",
                             "0012": "focus",
                             "0013": "focus",
                             "0014": "focus",
                             "0015": "focus",
                             "0086": "focus",
                             "0087": "focus",
                             "0088": "focus",
                             "0089": "focus",
                             "0090": "focus",
                             "0091": "focus",
                             "0092": "focus",
                             "0093": "focus",
                             "0094": "focus",
                             "0095": "focus",
                             "0096": "focus",
                             "0097": "focus",
                             "0108": "Acquisition",
                             "0109": "Acquisition",
                             "0110": "Acquisition",
                             "0115": "Acquisition",
                             "0116": "Acquisition",
                             "0117": "Acquisition",
                             "0118": "Acquisition",
                             "0125": "Acquisition",
                             "0126": "Acquisition",
                             "0127": "Acquisition",
                             "0128": "Acquisition",
                             "0129": "Acquisition",
                             "0130": "Acquisition",
                             "0131": "Acquisition",
                             "0132": "Acquisition",
                             "0133": "Acquisition",
                             "0134": "Acquisition",
                             "0135": "Acquisition",
                             "0141": "Acquisition",
                             "0142": "Acquisition",
                             "0143": "Acquisition",
                             "0144": "Acquisition",
                             "0146": "Test to best fit the mask",
                             "0151": "Acquisition",
                             "0152": "Acquisition",
                             "0153": "Acquisition",
                             "0154": "Acquisition",
                             },
              "2016-10-26": {"1041": "calibration flat-dummy",
                             "1042": "calibration flat-dummy",
                             "1043": "calibration flat-dummy",
                             "1095": "test : saturated in the red",
                             "1105": "no grating",
                             "0111": "lamp off - william",
                             "0112": "lamp off - william",
                             },
              "2016-10-28": {"1018": "calibration flat-dummy",
                             "0163": "started with mirror",
                             "0167": "seeing 0.71, science; saturated in the red",
                             "0171": "seeing 0,71, with mirror, without image",
                             "0176": "seeing 0,78, science low count, to check magnitude value (more fainter than expected)",
                             },
              "2016-10-30": {"1007": "bad flat TRIMSEC (William)",
                             "1008": "flat-dummy - CCD ROI mode: spectroscopy 1x1",
                             "1081": "problem image",
                             "1085": "clouds 1.65",
                             "1096": "---no grating -- mistake!!! 1.25",
                             "1103": "clouds, guide star lost during acquisition-- operador declaro: oficialmente negro! 1.13"
                             },
              "2016-10-31": {"0001": "test",
                             # TODO: Did not those focus as they have 0.46'' slit
                             # "0002": "focus",
                             # "0019": "focus",
                             "0020": "flat dummy",
                             "0021": "flat dummy",
                             "0022": "flat dummy",
                             # "0094": "NUVENS",
                             "0098": "teste",
                             },

              "2016-11-21": {"0018": "flat dummy",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             },
              "2016-11-22": {"0": "humidity was high all night, no observations were taken"
                             },

              "2017-03-02": {"0095": "obj 289 duplicated! spectra saturated",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             },
              "2017-03-26": {"0018": "Flat test",
                             "0019": "Flat test",
                             "0030": "Flat test",
                             "0089": "bad image",
                             "0107": "science. Saturated in central wavelength",
                             "0124": "error",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             },
              "2017-04-04": {"0018": "dummy_flat",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             },
              "2017-04-05": {"0018": "saturado",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             "0050": "Quartz lamp (flat) error",
                             },
              "2017-10-24": {"0018": "flat (error)",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             "0094": "no use, not sure which target is it",
                             },
              "2017-10-25": {"0018": "flat (error)",
                             # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                             },
              "2017-10-26": {"0020": "dummy flat",
                             "0084": "com erro",
                             "0086": "CuHeAr lampada, com erro",
                             "0088": "radial velocity star - estava com o braço",
                             "0114": "radial velocity star - estava com o braço",
                             "0115": "radial velocity star - estava com o braço",
                             "0126": "CuHeAr lampada, com erro",
                             "0127": "CuHeAr lampada, com erro",
                             },

              "2017-10-27": {
                  # TODO: 1-17 = Did not those focus as they have 0.46'' slit
                  "0079": "CuHeAr FAIL",
                  "0080": "CuHeAr FAIL",
                  "0085": "CuHeAr FAIL",
                  "0089": "Object, not lamp as in the header - william",
                  "0090": "CuHeAr FAIL",
                  "0094": "jellyfish in fornax",
                  "0095": "jellyfish in fornax",
                  "0096": "CuHeAr FAIL",
                  "0100 ": "CuHeAr FAIL",
              }
              }

bad_data = []

workdir = sys.argv[1]
night = re.findall("([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))", workdir)[0][0]

for fname in os.listdir(workdir):
    if '.fits' in fname:
        header = fits.getheader('%s/%s' % (workdir, fname), ignore_missing_end=True)
        if (header['SLIT'] != '1.03" long slit' and header['SLIT'] != '1.0" long slit') and (
                header['OBSTYPE'] != 'BIAS'):
            bad_data.append('mv %s/%s %s/bad_data/ # Bad SLIT: %s' % (workdir, fname, workdir, header["SLIT"]))
        else:
            for b in obslog_bad[night]:
                if fname.startswith(b):
                    bad_data.append('mv %s/%s %s/bad_data/ # Bad: %s' % (workdir, fname, workdir, obslog_bad[night][b]))

print("mkdir -p %s/bad_data" % workdir)
print("\n".join(bad_data))
