from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import shutil
import argparse
import glob
import logging
import matplotlib
matplotlib.use('Qt4Agg')

from .data_classifier import DataClassifier
from .night_organizer import NightOrganizer
from .image_processor import ImageProcessor

__author__ = 'David Sanmartim'
__date__ = '2016-07-15'
__version__ = "1.0b2"
__maintainer__ = "Simon Torres"
__email__ = "storres@ctio.noao.edu"

FORMAT = '%(levelname)s: %(asctime)s: %(module)s.%(funcName)s: %(message)s'
# DATE_FORMAT = '%m/%d/%Y %I:%M:%S%p'
DATE_FORMAT = '%I:%M:%S%p'
LOG_FILENAME = 'goodman_ccd.log'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)
# TODO (simon): Check the use of getLogger versus Logger
log = logging.getLogger('goodmanccd')


def get_args(arguments=None):
    """Get command line arguments.

    The list of arguments can be obtained by using the argument ``--help``.
    All the arguments start with two dashes and single-character arguments where
    avoided in order to eliminate confussion.

    Args:
        arguments (list): A list containing the arguments as elements.

    Returns:
        args (object): argparse instance. Contains all the arguments as
            attributes

    """

    parser = argparse.ArgumentParser(
        description="Goodman CCD Reduction - CCD reductions for Goodman "
                    "spectroscopic data.")

    parser.add_argument('--auto-clean',
                        action='store_true',
                        dest='auto_clean',
                        help="Automatically clean reduced data directory")

    parser.add_argument('--cosmic',
                        action='store',
                        dest='clean_cosmic',
                        default='dcr',
                        choices=['dcr', 'lacosmic', 'none'],
                        metavar='<method>',
                        help="Clean cosmic rays from all data. Options are: "
                             "'dcr', 'lacosmic' or 'none'. Default is 'dcr'. "
                             "See manual for full description of dcr.")

    parser.add_argument('--dcr-par-dir',
                        action='store',
                        default='files/',
                        metavar='<dcr.par_directory>',
                        dest='dcr_par_dir',
                        help="Directory of default dcr.par file")

    parser.add_argument('--debug',
                        action='store_true',
                        dest='debug_mode',
                        help="Show detailed information of the process.")

    # TODO (simon): Add argument to use calibration data from other day

    parser.add_argument('--flat-normalize',
                        action='store',
                        default='simple',
                        type=str,
                        metavar='<normalization_method>',
                        dest='flat_normalize',
                        choices=['mean', 'simple', 'full'],
                        help='Choose a method to normalize the master flat for'
                             'spectroscoy. Choices are: mean, simple (model) '
                             'and full (fits model to each line).')

    parser.add_argument('--flat-norm-order',
                        action='store',
                        default=15,
                        type=int,
                        metavar='<order>',
                        dest='norm_order',
                        help='Defines the order of the model to be fitted. '
                             'Default to 15')

    parser.add_argument('--ignore-bias',
                        action='store_true',
                        dest='ignore_bias',
                        help="Ignore bias correction")

    parser.add_argument('--ignore-flats',
                        action='store_true',
                        dest='ignore_flats',
                        help="Ignore flat field correction")

    parser.add_argument('--keep-cosmic-files',
                        action='store_false',
                        dest='keep_cosmic_files',
                        help="After cleaning cosmic rays with dcr, do not "
                             "remove the input file and the cosmic rays file.")

    parser.add_argument('--log-file',
                        action='store',
                        dest='log_file',
                        metavar='<log_file>',
                        default=LOG_FILENAME,
                        help="Name for log file. "
                             "Default name is {:s}. "
                             "The file is written in <red_path> and will be "
                             "deleted each time you run this "
                             "program".format(LOG_FILENAME))

    parser.add_argument('--raw-path',
                        action='store',
                        metavar='<raw_path>',
                        default='./',
                        type=str,
                        help="Path to raw data.")

    parser.add_argument('--red-path',
                        action='store',
                        metavar='<red_path>',
                        type=str,
                        default='./RED',
                        help="Path to reduced data.")

    parser.add_argument('--saturation',
                        action='store',
                        default=65000.,
                        dest='saturation_limit',
                        metavar='<value>',
                        help="Saturation limit. Default to 65.000 ADU (counts)")

    args = parser.parse_args(args=arguments)

    # define log file
    # the log file will be stored in the same directory that the program
    # is called
    log.info('Logging to file {:s}'.format(LOG_FILENAME))
    file_handler = logging.FileHandler(filename=LOG_FILENAME)
    file_handler.setLevel(level=logging.INFO)
    formatter = logging.Formatter(fmt=FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(fmt=formatter)
    log.addHandler(file_handler)

    if args.debug_mode:
        log.info('Changing log level to DEBUG.')
        log.setLevel(level=logging.DEBUG)
    if os.path.isdir(args.raw_path):
        args.raw_path = os.path.abspath(args.raw_path)
        log.debug(os.path.abspath(args.raw_path))
    else:
        parser.print_help()
        parser.exit("Raw data folder doesn't exist")

    # updated full path for default dcr.par file. If it doesn't exist it will
    # create an empty one.
    dcr_par_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 args.dcr_par_dir)
    if not os.path.isdir(dcr_par_full_path) or args.dcr_par_dir != 'files/':
        log.info("dcr.par default location doesn't exist.")
        try:
            os.path.os.makedirs(dcr_par_full_path)
            log.info('Created dcr.par empty directory: %s', dcr_par_full_path)
            args.dcr_par_dir = dcr_par_full_path
        except OSError as err:
            log.error(err)
    else:
        args.dcr_par_dir = dcr_par_full_path
    # print_default_args(args)
    return args


class MainApp(object):

    def __init__(self, args=None):
        """This method initializes the MainApp class

        The main task of this method is to call the get_args function that
        returns an argparse object.
        The arguments will be obtained here and they will be available for all
        execution of the program.
        Other attributes will be initialized as None.

        Args:
            args (list): a list of arguments and values, this is useful when you
                want to import the class.
        """
        if args is None:
            self.args = get_args()
        else:
            self.args = args
        self.data_container = None
        self.full_path = None
        # self.instrument = None
        # self.technique = None
    
    def __call__(self):
        """Call method for MainApp

        From the arguments this method finds the raw_path attribute and checks
        its contents for the existance of files containing the '.fits' string.
        If there is none it will assume every item is a different data directory
        and they will be treated independently. If there are '.fits' files the
        program will assume is a single data directory.
        Any subdirectory will be ignored.

        """

        folders = glob.glob(os.path.join(self.args.raw_path, '*'))
        if any('.fits' in item for item in folders):
            folders = [self.args.raw_path]
        for data_folder in folders:
            if not os.path.isdir(data_folder):
                continue

            self.args.raw_path = data_folder

            try:
                log.debug('Initializing DataClassifier Class')
                night_sorter = DataClassifier(self.args)
                log.debug('Calling night_sorter Instance of DataClassifier')
                night_sorter()
                # self.instrument = night_sorter.instrument
                # self.technique = night_sorter.technique
                # print(self.instrument)
                # print(self.technique)
            except AttributeError as error:
                log.error(error)
                log.error('Empty or Invalid data directory:'
                          '{:s}'.format(data_folder))
                continue

            # # check start
            # self.args.raw_path = data_folder
            if self.args.red_path == './RED' or len(folders) > 1:

                log.info('No special reduced data path defined. '
                         'Proceeding with defaults.')

                if self.args.raw_path not in self.args.red_path:
                    self.args.red_path = os.path.join(self.args.raw_path, 'RED')
                    # print(self.args.red_path)

            if os.path.isdir(self.args.red_path):
                if os.listdir(self.args.red_path) != []:
                    log.warning('Reduced Data Path is not empty')
                    if self.args.auto_clean:
                        for _file in os.listdir(self.args.red_path):
                            try:
                                os.unlink(os.path.join(self.args.red_path,
                                                       _file))
                            except OSError as error:
                                log.error('OSError: {:s}'.format(error))
                                log.warning('Removing Directory '
                                            '{:s}'.format(_file))

                                shutil.rmtree(os.path.join(self.args.red_path,
                                                           _file))

                        log.info('Cleaned Reduced data directory:'
                                 ' {:s}'.format(self.args.red_path))
                    else:
                        log.error('Please clean the reduced data folder or '
                                  'use --auto-clean')
                        break
                self.args.red_path = os.path.abspath(self.args.red_path)
                log.debug(os.path.abspath(self.args.red_path))
            else:
                try:
                    log.warning("Reduction folder doesn't exist.")
                    os.mkdir(os.path.abspath(self.args.red_path))
                    log.info('Created reduced data directory!')
                    log.info(os.path.abspath(self.args.red_path))
                except OSError as error:
                    log.error(error)
            # check ends

            # print(night_sorter.nights_dict)
            for night in night_sorter.nights_dict:
                nd = night_sorter.nights_dict[night]
                log.debug('Initializing NightOrganizer Class')
                night_organizer = NightOrganizer(
                    full_path=nd['full_path'],
                    instrument=nd['instrument'],
                    technique=nd['technique'],
                    ignore_bias=self.args.ignore_bias,
                    ignore_flats=self.args.ignore_flats)

                log.debug('Calling night_organizer instance')
                self.data_container = night_organizer()
                if self.data_container is None or self.data_container is None:
                    log.error('Discarding night ' + str(night))
                    break
                process_images = ImageProcessor(self.args, self.data_container)
                process_images()


if __name__ == '__main__':
    main_app = MainApp()
    main_app()
