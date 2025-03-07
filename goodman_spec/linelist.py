# -*- coding: utf8 -*-
""" Line list per elements

This contains a dictionary of elements used for comparison lamps with their
main emission lines

The current elements present are:

    Hg: Mercury
    Ar: Argon
    Cu: Copper
    Ne: Neon
    He: Helium
    CuAr: Copper Argon

"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import logging
import pandas
import os
import ccdproc
import re

# FORMAT = '%(levelname)s:%(filename)s:%(module)s: 	%(message)s'
# log.basicConfig(level=log.DEBUG, format=FORMAT)
log = logging.getLogger('redspec.linelist')


class ReferenceData(object):
    """Contains spectroscopic reference lines values and filename to templates.

    This class stores:
        - file names for reference fits spectrum
        - file names for CSV tables with reference lines and relative intensities
        - line positions only for the elements used in SOAR comparison lamps
    """
    def __init__(self, reference_dir):
        """Init method for the ReferenceData class

        This methods uses ccdproc.ImageFileCollection on the reference_dir to
        capture all possible reference lamps. Also defines dictionaries
        containg line lists for several elements used in lamps.

        Args:
            reference_dir (str): full path to the reference data directory
        """
        self.reference_dir = reference_dir
        reference_collection = ccdproc.ImageFileCollection(self.reference_dir)
        self.ref_lamp_collection = reference_collection.summary.to_pandas()
        self.lamps_file_list = {'cuhear': 'goodman_comp_600_BLUE_CuHeAr.fits',
                                'hgar': 'goodman_comp_400_M2_GG455_HgAr.fits',
                                'hgarne': 'goodman_comp_400_M2_GG455_HgArNe.fits'}
        self.line_list_files = {'cu': 'Cu_3000A-10000A_clean.csv',
                                'he': 'He_3000A-10000A_clean.csv',
                                'ne': 'Ne_3000A-10000A_clean.csv',
                                'ar': 'Ar_3000A-10000A_clean.csv',
                                'hg': 'Hg_3000A-10000A_clean.csv'}

        self.line_list = {'hg': [3125.67,
                                 3131.70,
                                 3341.48,
                                 3650.153,
                                 3654.84,
                                 3663.279,
                                 4046.563,
                                 4077.831,
                                 4358.327,
                                 4916.068,
                                 5460.750,
                                 5769.598,
                                 5790.663],
                          'cu': [1999.698,
                                 2035.854,
                                 2037.127,
                                 2043.802,
                                 2135.981,
                                 2165.09,
                                 2178.94,
                                 2179.410,
                                 2181.72,
                                 2189.630,
                                 2192.268,
                                 2199.58,
                                 2210.268,
                                 2214.58,
                                 2218.108,
                                 2225.70,
                                 2227.78,
                                 2230.08,
                                 2242.618,
                                 2244.26,
                                 2247.002,
                                 2263.08,
                                 2293.84,
                                 2392.63,
                                 2406.66,
                                 2441.64,
                                 2492.15,
                                 2618.37,
                                 2689.300,
                                 2700.962,
                                 2703.184,
                                 2713.508,
                                 2718.778,
                                 2766.37,
                                 2769.669,
                                 2877.100,
                                 2961.16,
                                 3036.10,
                                 3063.41,
                                 3108.60,
                                 3194.10,
                                 3243.16,
                                 3247.54,
                                 3273.96,
                                 3290.54,
                                 3307.95,
                                 3337.84,
                                 3530.38,
                                 3686.555,
                                 4062.64,
                                 4651.12,
                                 4909.734,
                                 4931.698,
                                 4953.724,
                                 5051.793,
                                 5105.54,
                                 5153.24,
                                 5218.20,
                                 5292.52,
                                 5700.24,
                                 5782.13,
                                 6000.120,
                                 6150.384,
                                 6154.222,
                                 6216.939,
                                 6219.844,
                                 6273.349,
                                 6301.009,
                                 6377.840,
                                 6423.884,
                                 6448.559,
                                 6470.168,
                                 6481.437,
                                 6624.292,
                                 6641.396,
                                 7404.354,
                                 7652.333,
                                 7664.648,
                                 7778.738,
                                 7805.184,
                                 7807.659,
                                 7825.654,
                                 7902.553,
                                 7933.13,
                                 7988.163,
                                 8092.63,
                                 8283.160,
                                 8511.061,
                                 9861.280,
                                 9864.137,
                                 10054.938],
                          'ne': [5852.488,
                                 5881.895,
                                 5944.834,
                                 5975.534,
                                 6029.997,
                                 6074.337,
                                 6096.163,
                                 6128.450,
                                 6143.062,
                                 6163.594,
                                 6217.281,
                                 6266.495,
                                 6304.789,
                                 6334.428,
                                 6382.991,
                                 6402.246,
                                 6506.528,
                                 6532.882,
                                 6598.953,
                                 6652.092,
                                 6678.276,
                                 6717.043,
                                 6929.467,
                                 7024.050,
                                 7032.413,
                                 7173.938,
                                 7245.166,
                                 7438.898,
                                 7488.871,
                                 7535.774,
                                 7544.044,
                                 7943.180,
                                 8082.457,
                                 8136.406,
                                 8300.324,
                                 8377.606,
                                 8418.426,
                                 8495.359,
                                 8591.258,
                                 8634.647,
                                 8654.384,
                                 8853.867,
                                 8865.756,
                                 8919.499,
                                 8988.58,
                                 9148.68,
                                 9201.76,
                                 9300.85,
                                 9313.98,
                                 9326.52,
                                 9354.218,
                                 9425.38,
                                 9459.21,
                                 9486.680,
                                 9534.167,
                                 9547.40,
                                 9665.424],
                          'he': [3187.745,
                                 3354.55,
                                 3613.643,
                                 3819.6072,
                                 3888.648,
                                 3964.7289,
                                 4009.268,
                                 4120.815,
                                 4168.967,
                                 4437.551,
                                 4471.479,
                                 4713.1455,
                                 4921.931,
                                 5015.6779,
                                 5047.738,
                                 5875.621,
                                 7281.349,
                                 10830.337],
                          'ar': [3093.4019,
                                 3139.0176,
                                 3161.3726,
                                 3169.6685,
                                 3181.0376,
                                 3204.3210,
                                 3243.6887,
                                 3249.8003,
                                 3281.7016,
                                 3307.2283,
                                 3350.9243,
                                 3376.4359,
                                 3388.5309,
                                 3454.0952,
                                 3476.7474,
                                 3478.2324,
                                 3480.5055,
                                 3499.4765,
                                 3509.7785,
                                 3514.3877,
                                 3519.9936,
                                 3521.2601,
                                 3521.9781,
                                 3535.3196,
                                 3548.5144,
                                 3554.3058,
                                 3556.9041,
                                 3559.5081,
                                 3561.0304,
                                 3565.0298,
                                 3567.6564,
                                 3576.6156,
                                 3581.6084,
                                 3582.3546,
                                 3588.4407,
                                 3605.8792,
                                 3606.5218,
                                 3622.1375,
                                 3632.6831,
                                 3637.0310,
                                 3639.8329,
                                 3649.8323,
                                 3650.8896,
                                 3655.2782,
                                 3656.0498,
                                 3659.5289,
                                 3660.437,
                                 3669.6024,
                                 3671.0048,
                                 3673.2645,
                                 3678.2701,
                                 3680.0609,
                                 3682.5448,
                                 3690.8951,
                                 3706.9302,
                                 3709.9088,
                                 3714.7337,
                                 3717.1713,
                                 3718.2065,
                                 3720.4265,
                                 3724.5165,
                                 3729.3087,
                                 3737.889,
                                 3746.4476,
                                 3750.4799,
                                 3753.5177,
                                 3754.0498,
                                 3763.5053,
                                 3765.27,
                                 3766.1186,
                                 3770.52,
                                 3780.8398,
                                 3786.3824,
                                 3796.5934,
                                 3799.382,
                                 3803.1724,
                                 3808.5748,
                                 3809.4561,
                                 3819.0159,
                                 3825.6729,
                                 3826.8072,
                                 3834.6787,
                                 3841.5187,
                                 3844.7311,
                                 3845.4055,
                                 3850.5813,
                                 3856.1382,
                                 3861.747,
                                 3868.5284,
                                 3872.1371,
                                 3875.2645,
                                 3880.3332,
                                 3891.4017,
                                 3891.9792,
                                 3894.66,
                                 3895.2502,
                                 3900.6266,
                                 3911.576,
                                 3914.7675,
                                 3925.7188,
                                 3926.0456,
                                 3928.6233,
                                 3931.2359,
                                 3932.5466,
                                 3944.2717,
                                 3946.0971,
                                 3947.5046,
                                 3948.9789,
                                 3952.7291,
                                 3958.38,
                                 3968.3594,
                                 3974.4766,
                                 3974.759,
                                 3979.3559,
                                 3979.7155,
                                 3988.1576,
                                 3992.0535,
                                 3994.7918,
                                 3999.252,
                                 4001.1379,
                                 4005.3628,
                                 4011.2093,
                                 4013.8566,
                                 4019.8429,
                                 4022.629,
                                 4031.3783,
                                 4033.8093,
                                 4035.46,
                                 4038.8043,
                                 4042.8937,
                                 4044.4179,
                                 4045.6773,
                                 4045.9654,
                                 4047.4815,
                                 4052.9208,
                                 4054.5258,
                                 4062.641,
                                 4063.238,
                                 4070.7835,
                                 4072.0047,
                                 4072.3849,
                                 4076.6284,
                                 4076.9432,
                                 4079.5738,
                                 4082.3872,
                                 4099.4563,
                                 4103.9121,
                                 4112.8153,
                                 4116.3753,
                                 4128.64,
                                 4129.6823,
                                 4131.7235,
                                 4144.2435,
                                 4156.086,
                                 4158.5905,
                                 4164.1795,
                                 4168.9682,
                                 4178.3658,
                                 4179.2973,
                                 4181.8836,
                                 4189.6511,
                                 4190.7129,
                                 4191.0294,
                                 4198.317,
                                 4199.8891,
                                 4200.6745,
                                 4201.5549,
                                 4201.9715,
                                 4203.4109,
                                 4217.4308,
                                 4218.6649,
                                 4222.6373,
                                 4226.6089,
                                 4226.9876,
                                 4228.158,
                                 4229.8696,
                                 4237.2198,
                                 4248.956,
                                 4251.1846,
                                 4255.6034,
                                 4259.3619,
                                 4266.2864,
                                 4266.5271,
                                 4272.1689,
                                 4277.5282,
                                 4282.8976,
                                 4297.9645,
                                 4300.1008,
                                 4300.6495,
                                 4309.2392,
                                 4331.1995,
                                 4332.0297,
                                 4333.5612,
                                 4335.3379,
                                 4337.0708,
                                 4338.2314,
                                 4345.168,
                                 4345.8966,
                                 4348.064,
                                 4352.2049,
                                 4362.0662,
                                 4363.7945,
                                 4367.8316,
                                 4370.7532,
                                 4371.329,
                                 4372.49,
                                 4374.8579,
                                 4375.9542,
                                 4379.6668,
                                 4382.928,
                                 4383.7535,
                                 4385.0566,
                                 4386.9656,
                                 4397.7971,
                                 4400.0968,
                                 4400.9863,
                                 4401.755,
                                 4404.9022,
                                 4406.4704,
                                 4420.9124,
                                 4423.9944,
                                 4426.0011,
                                 4430.189,
                                 4430.9963,
                                 4433.838,
                                 4438.1175,
                                 4439.4614,
                                 4439.8793,
                                 4440.1216,
                                 4445.8483,
                                 4448.4597,
                                 4448.8792,
                                 4449.5206,
                                 4460.5574,
                                 4474.7594,
                                 4480.35,
                                 4481.8107,
                                 4490.9816,
                                 4498.5384,
                                 4502.9268,
                                 4507.8339,
                                 4509.374,
                                 4510.7332,
                                 4522.323,
                                 4530.5523,
                                 4530.785,
                                 4535.4903,
                                 4537.6426,
                                 4543.8692,
                                 4545.0519,
                                 4547.7589,
                                 4561.0128,
                                 4563.7429,
                                 4564.4054,
                                 4579.3495,
                                 4589.8978,
                                 4596.0967,
                                 4598.7627,
                                 4609.5673,
                                 4628.4409,
                                 4637.2328,
                                 4651.124,
                                 4657.9012,
                                 4682.2759,
                                 4702.3161,
                                 4721.5910,
                                 4726.8683,
                                 4732.0532,
                                 4735.9058,
                                 4764.8646,
                                 4806.0205,
                                 4847.8095,
                                 4865.9105,
                                 4876.2611,
                                 4879.8635,
                                 4882.2432,
                                 4888.2612,
                                 4889.0422,
                                 4904.7516,
                                 4914.3146,
                                 4933.2091,
                                 4942.9214,
                                 4965.0795,
                                 4972.1597,
                                 5009.3344,
                                 5017.1628,
                                 5062.0371,
                                 5090.4951,
                                 5118.2023,
                                 5125.7654,
                                 5141.7827,
                                 5145.3083,
                                 5151.3907,
                                 5162.2846,
                                 5165.7728,
                                 5176.2292,
                                 5187.7462,
                                 5216.8139,
                                 5218.2020,
                                 5221.2710,
                                 5254.4648,
                                 5421.3517,
                                 5439.9891,
                                 5442.2427,
                                 5443.6893,
                                 5451.6520,
                                 5457.4157,
                                 5467.1608,
                                 5473.4516,
                                 5490.1194,
                                 5495.8738,
                                 5498.1841,
                                 5506.1128,
                                 5524.9570,
                                 5558.7020,
                                 5572.5413,
                                 5577.6845,
                                 5581.8714,
                                 5588.7200,
                                 5597.4756,
                                 5601.1216,
                                 5606.7330,
                                 5641.3751,
                                 5648.6863,
                                 5650.7043,
                                 5659.1272,
                                 5681.9001,
                                 5691.6612,
                                 5700.8730,
                                 5738.3869,
                                 5739.5196,
                                 5772.1143,
                                 5774.0087,
                                 5783.5360,
                                 5802.0798,
                                 5834.2633,
                                 5860.3103,
                                 5882.6242,
                                 5888.5841,
                                 5912.0853,
                                 5916.5992,
                                 5927.1258,
                                 5928.8130,
                                 5942.6686,
                                 5949.2583,
                                 5971.6008,
                                 5998.9987,
                                 6005.7242,
                                 6013.6777,
                                 6025.1500,
                                 6032.1274,
                                 6043.2233,
                                 6046.8977,
                                 6052.7229,
                                 6059.3725,
                                 6064.7508,
                                 6081.2433,
                                 6085.8797,
                                 6090.7848,
                                 6098.8031,
                                 6101.1615,
                                 6103.5390,
                                 6105.6351,
                                 6113.4657,
                                 6114.9234,
                                 6119.6565,
                                 6123.3619,
                                 6127.4160,
                                 6128.7227,
                                 6145.4411,
                                 6155.2385,
                                 6165.1232,
                                 6170.1740,
                                 6173.0964,
                                 6174.4032,
                                 6212.5031,
                                 6215.9383,
                                 6243.1201,
                                 6296.8722,
                                 6307.6570,
                                 6333.1459,
                                 6357.0229,
                                 6364.8937,
                                 6369.5748,
                                 6384.7169,
                                 6396.6097,
                                 6399.2065,
                                 6403.0128,
                                 6416.3071,
                                 6418.3703,
                                 6431.5550,
                                 6437.6003,
                                 6441.8994,
                                 6443.8598,
                                 6466.5526,
                                 6468.0483,
                                 6472.4294,
                                 6481.1453,
                                 6483.0825,
                                 6493.9694,
                                 6499.1061,
                                 6538.1120,
                                 6604.8534,
                                 6620.9665,
                                 6632.0837,
                                 6638.2207,
                                 6639.7403,
                                 6643.6976,
                                 6656.9386,
                                 6660.6761,
                                 6664.0510,
                                 6666.3588,
                                 6677.2817,
                                 6684.2929,
                                 6719.2184,
                                 6752.8335,
                                 6756.1631,
                                 6766.6117,
                                 6827.2488,
                                 6861.2688,
                                 6863.5350,
                                 6871.2891,
                                 6879.5824,
                                 6888.1742,
                                 6937.6642,
                                 6951.4776,
                                 6965.4307,
                                 7030.2514,
                                 7067.2181,
                                 7147.0416,
                                 7206.9804,
                                 7272.9359,
                                 7311.7159,
                                 7353.2930,
                                 7372.1184,
                                 7383.9805,
                                 7503.8691,
                                 7514.6518,
                                 7635.1060,
                                 7723.7611,
                                 7724.2072,
                                 7948.1764,
                                 8006.1567,
                                 8014.7857,
                                 8103.6931,
                                 8115.311,
                                 8264.5225,
                                 8408.2096,
                                 8424.6475,
                                 8521.4422,
                                 8667.9442,
                                 9122.9674,
                                 9224.4992,
                                 9354.2198,
                                 9657.7863,
                                 9784.5028,
                                 10470.0535]}

    def get_line_list_by_name(self, lamp_name):
        """Get the reference lines for elements in the lamp's name

        Splits the name in chunks of two characters assuming each one of them
        represents an element in the comparison lamp, then fetches the list of
        line positions available and appends it to a list that will be return
        ordered.

        Args:
            lamp_name (str): Lamp's name as in the header keyword OBJECT.

        Returns:
            line_list(list): Sorted line list.

        """
        elements = [lamp_name[i:i + 2].lower() for i in range(0, len(lamp_name), 2)]
        line_list = []
        for element in elements:
            line_list.extend(self.line_list[element])
        return sorted(line_list)

    def get_lines_in_range(self, blue, red, lamp_name):
        """Get the reference lines for a given comparison lamp in a wavelength
        range

        Select the reference lines available for all the elements in the
        comparison lamp in the spectral range specified by blue and red

        Args:
            blue(float): Blue limit for lines required.
            red(float): Red limit for lines required.
            lamp_name(str): Lamp's name as in the header keyword OBJECT.

        Returns:
            lines(list): Sorted line list.
        """
        lines = []
        if len(lamp_name) % 2 == 0:
            for element_index in range(0, len(lamp_name), 2):
                element = lamp_name[element_index:element_index + 2]
                all_lines = self.line_list[element]
                for line in all_lines:
                    if blue <= line <= red:
                        lines.append(line)
        return sorted(lines)

    def get_reference_lamps_by_name(self, lamp_name):
        """Get lamp's template by element

        Some lamp templates are available for selected configurations.

        Notes:
            This method has hardcoded lamp names. Also it might be deprecated
            in the near future.

        Args:
            lamp_name(str): Lamp's name as in the header keyword OBJECT

        Returns:
            reference_lamp(str): Full path to reference lamps
        """
        lamp_name = lamp_name.lower()
        # TODO (simon): Do this using ImageFileCollection
        try:
            reference_lamp = os.path.join(self.reference_dir,
                                          self.lamps_file_list[lamp_name])

            return reference_lamp
        except KeyError:
            log.error('Reference lamp %s does not exist', lamp_name)
            return None

    def get_best_reference_lamp(self, header):
        """Finds a suitable template lamp from the catalog

        Args:
            header (object): FITS header of image we are looking a a reference
                lamp.

        Returns:
            full path to best matching reference lamp.

        """
        criteria = ['slit', 'cam_targ', 'grt_targ', 'grating', 'object']

        lamp_pandas_data_frame = self.ref_lamp_collection[
            self.ref_lamp_collection['object'] == header['object']]

        # print(lamp_pandas_data_frame)
        if len(lamp_pandas_data_frame) > 1:
            while len(lamp_pandas_data_frame) > 1:
                # print(lamp_pandas_data_frame.file)
                keyword_to_filter = criteria.pop()
                # print('Filter: ' + keyword_to_filter)
                lamp_pandas_data_frame = lamp_pandas_data_frame[
                    (lamp_pandas_data_frame[keyword_to_filter] == header[keyword_to_filter])]
            # else:
            #     print(lamp_pandas_data_frame)

        elif len(lamp_pandas_data_frame) == 1:
            log.debug(lamp_pandas_data_frame.file.tolist()[0])
        else:
            log.error('There is no reference lamp found')
            raise NotImplementedError('Reference Lamp not found')
        try:
            lamp_name = lamp_pandas_data_frame.file.tolist()[0]
            ref_lamp_full_path = os.path.join(self.reference_dir, lamp_name)
            log.debug('Reference Lamp Full Path' + ref_lamp_full_path)
            return ref_lamp_full_path
        except IndexError:
            raise NotImplementedError('No lamp found in reference files.')

    def get_exact_lamp(self, header):
        """Finds the exact reference lamp

        Args:
            header (object): FITS header of image we are looking a a reference
                lamp.

        Returns:
            full path to best matching reference lamp.

        """
        criteria = ['slit', 'cam_targ', 'grt_targ', 'grating', 'object']

        lamp_file_list = self.ref_lamp_collection.file[
            ((self.ref_lamp_collection['grt_targ'] == header['grt_targ']) &
             (self.ref_lamp_collection['cam_targ'] == header['cam_targ']) &
             (self.ref_lamp_collection['grating'] == header['grating']) &
             (self.ref_lamp_collection['object'] == header['object']))].tolist()

        if len(lamp_file_list) == 1:
            # print(lamp_file_list)
            return os.path.join(self.reference_dir, lamp_file_list[0])
        else:
            raise NotImplementedError

    def get_ref_spectrum_from_linelist(self, blue, red, name):
        """Build spectrum from linelist

        Builds a unidimensional spectrum to be used as a template for finding
        an automatic wavelength solution.

        There is no safe way to do this, so this method will be deprecated at
        some point.

        Notes:
            Experimental, never really worked.

        """
        # raise DeprecationWarning
        if len(name) % 2 == 0:
            elements = [name[i:i + 2].lower() for i in range(0, len(name), 2)]
            for element in elements:
                linelist_file = self.line_list_files[element]
                pandas_data_frame = pandas.read_csv(self.reference_dir + linelist_file)
                # print(linelist_file, pandas_data_frame, blue, red)

        else:
            log.error('Error in the calibration lamp name: %s', name)
            return None
