#!/usr/bin/env python2
# -*- coding: utf8 -*-
"""Pipeline for GOODMAN spectra Extraction.

This program finds reduced images, i.e. trimmed, bias subtracted, flat fielded,
etc. that match the <pattern> in the source folder, then classify them in two
groups: Science or Lamps. For science images, finds the spectrum or spectra and
traces it doing some fit.
Simon Torres 2016-06-28

"""
# TODO (simon): Change all astropy.io.fits to astropy.CCDData.read
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import os
import textwrap
import argparse
import logging
import matplotlib
matplotlib.use('Qt4Agg')
import warnings
from .wavelength import WavelengthCalibration, process_spectroscopy_data
from goodman_ccd.core import (classify_spectroscopic_data)


warnings.filterwarnings('ignore')
FORMAT = '%(levelname)s: %(asctime)s:%(module)s.%(funcName)s: %(message)s'
DATE_FORMAT = '%I:%M:%S%p'
LOG_FILENAME = 'goodman_spec.log'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)
# TODO (simon): Check the use of getLogger versus Logger
log = logging.getLogger('redspec')

__author__ = 'Simon Torres'
__date__ = '2016-06-28'
__version__ = "0.1"
__email__ = "storres@ctio.noao.edu"
__status__ = "Development"


def get_args(arguments=None):
    """Handles the argparse library and returns the arguments

    The list of arguments can be found with running `redspec -h`.

    Notes:
        The full list of arguments are not listed here as the may evolve in
        which case is impossible to keep this up to date.


    Returns:
        An object that contains all the variables parsed through the argument
        system

    """
    leave = False
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            '''Extracts goodman spectra and does wavelength calibration.'''))

    parser.add_argument('--data-path',
                        action='store',
                        default='./',
                        type=str,
                        metavar='<Source Path>',
                        dest='source',
                        help='Path for location of raw data. Default <./>')

    parser.add_argument('--proc-path',
                        action='store',
                        default='./',
                        type=str,
                        metavar='<Destination Path>',
                        dest='destiny',
                        help='Path for destination of processed data. Default '
                             '<./>')

    parser.add_argument('--search-pattern',
                        action='store',
                        default='cfzsto',
                        type=str,
                        metavar='<Search Pattern>',
                        dest='pattern',
                        help="Pattern for matching the goodman's reduced data.")

    parser.add_argument('--output-prefix',
                        action='store',
                        default='g',
                        metavar='<Out Prefix>',
                        dest='output_prefix',
                        help="Prefix to add to calibrated spectrum.")

    parser.add_argument('--extraction',
                        action='store',
                        default='simple',
                        type=str,
                        metavar='<Extraction Type>',
                        dest='extraction_type',
                        choices=['simple', 'optimal'],
                        help='Choose a which extraction to perform. Simple is a '
                             'sum across the spatial direction after the '
                             'background has been removed. Optimal is a more '
                             'advanced method that considers weights and profile'
                             'fitting.')

    parser.add_argument('--reference-files',
                        action='store',
                        default='refdata/',
                        metavar='<Reference Dir>',
                        dest='reference_dir',
                        help="Directory of Reference files location")

    parser.add_argument('--interactive',
                        action='store_true',
                        dest='interactive_ws',
                        help="Interactive wavelength solution."
                             "Disbled by default.")

    parser.add_argument('--debug',
                        action='store_true',
                        dest='debug_mode',
                        help="Debugging Mode")

    parser.add_argument('--log-to-file',
                        action='store_true',
                        dest='log_to_file',
                        help="Write log to a file")

    parser.add_argument('--max-targets',
                        action='store',
                        dest='max_n_targets',
                        metavar='<max targets>',
                        type=int,
                        default=3,
                        help="Maximum number of targets to be found in a "
                             "single image. Default 3")

    parser.add_argument('--save-plots',
                        action='store_true',
                        dest='save_plots',
                        help="Save all plots in a directory")

    parser.add_argument('--plot-results',
                        action='store_true',
                        dest='plot_results',
                        help="Show wavelength calibrated spectrum at the end.")

    args = parser.parse_args(args=arguments)

    if args.log_to_file:
        log.info('Logging to file {:s}'.format(LOG_FILENAME))
        file_handler = logging.FileHandler(LOG_FILENAME)
        formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(fmt=formatter)
        log.addHandler(file_handler)

    if args.debug_mode:
        log.info('Changing log level to DEBUG.')
        log.setLevel(level=logging.DEBUG)

    # get full path for reference files directory
    ref_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 args.reference_dir)
    if not os.path.isdir(ref_full_path):
        log.info("Reference files directory doesn't exist.")
        try:
            os.path.os.makedirs(ref_full_path)
            log.info('Reference Files Directory is: %s', ref_full_path)
            args.reference_dir = ref_full_path
        except OSError as err:
            log.error(err)
    else:
        args.reference_dir = ref_full_path

    if not os.path.isdir(args.source):
        leave = True
        log.error("Source Directory doesn't exist.")

    if not os.path.isdir(args.destiny):
        leave = True
        log.error("Destination folder doesn't exist.")
        try:
            os.path.os.makedirs(args.destiny)
            log.info('Destination folder created: %s', args.destiny)
        except OSError as err:
            log.error(err)

    if leave:
        parser.print_help()
        parser.exit("Leaving the Program.")
    # print_default_args(args)
    return args


class MainApp(object):
    """Defines and initialize all important variables for processing the data

    The MainApp class controls the way the night is organized for further
    processing. It also sets the appropriate parameters that will allow for a
    smooth working in all the other modules.

    """
    def __init__(self, args=None):
        """Init method for MainApp class

        This method initializes the arguments for the class, if they are not
        provided it will get them.

        Args:
            args (object): argparse.Namespace instance that contains all the
                arguments.
        """

        if args is None:
            self.args = get_args()
        else:
            self.args = args

        self.wavelength_solution_obj = None

    def __call__(self):
        """Call method for the MainApp class

        This method call the higher level functions in order to do the
        spectroscopic data reduction.

        """

        # data_container instance of NightDataContainer defined in core
        data_container = classify_spectroscopic_data(
            path=self.args.source,
            search_pattern=self.args.pattern)

        # print('data_container.bias')
        # print(data_container.bias)
        # print('data_container.day_flats')
        # print(data_container.day_flats)
        # print('data_container.dome_flats')
        # print(data_container.dome_flats)
        # print('data_container.sky_flats')
        # print(data_container.sky_flats)
        # print('data_container.data_groups')
        # print(data_container.data_groups)
        # print('data_container.spec_groups')
        # print(data_container.spec_groups)

        self.wavelength_solution_obj = process_spectroscopy_data(
            data_container=data_container,
            args=self.args,
            extraction_type=self.args.extraction_type)


if __name__ == '__main__':
    MAIN_APP = MainApp()
    try:
        MAIN_APP()
    except KeyboardInterrupt:
        sys.exit(0)
