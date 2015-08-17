

__author__ = 'Colin Summers'
__copyright__ = 'Copyright 2015, Ginger Lab'
__maintainer__ = 'Colin Summers'
__email__ = 'colinxs@uw.edu'
__status__ = 'Development'

import os
import ss_device
import matplotlib
matplotlib.use('Agg')
import numpy as np
import jv_calculations


def get_dir_path():
    """
    Gets a director path from the user, checking if path given is a valid
    directory (i.e. exists and is not a file).

    Returns
    ----------
    str
        valid pathname of a directory
    """
    print 'Give me the path to the directory containing JV data as .txt files'
    path = raw_input('>')
    if os.path.exists(path) and not os.path.isfile(path):
        return os.path.normpath(path)
    else:
        print 'Path doesn\'t exist or points to a file, not a directory'
        return get_dir_path()


class HandleFileSave(object):
    """
    This class implements the context manager protocol as defined by
    https://www.python.org/dev/peps/pep-0343/. It is a modification to
    the built-in 'open()' function. It will generate a new file object,
    avoiding file collisions if indicated, and handle file overwrites
    on files that are locked (i.e. open in another program).

    Attributes
    ----------
    path : str
        desired path for new file object
    overwrite : bool
        True if file overwrite is desired, false otherwise
    file_handler : file object
        file handle of new file to save

    """
    def __init__(self, path, overwrite):
        self.path = os.path.normpath(path)
        self.overwrite = overwrite
        self.file_handler = None

    def _open(self):
        if os.path.isfile(self.path):
            if self.overwrite:
                self._open_recursive(self.path)
            else:
                n = 1
                path = self.path
                while os.path.isfile(path):
                    path = self._modify_filename(n)
                    n += 1
                self._open_recursive(path)
        else:
            self._open_recursive(self.path)

    def _open_recursive(self, path, n=1):
        try:
            self.file_handler = open(path, 'wb')
            print 'Saving \'{}\''.format(path)
        except EnvironmentError:
            path = self._modify_filename(n)
            n += 1
            self._open_recursive(path, n)

    def __enter__(self):
        self._open()
        if self.file_handler is None:
            raise TypeError('self.file_handler never set.')
        return self.file_handler

    def __exit__(self, exc_type, exc_value, traceback):
        self.file_handler.close()

    # pylint: disable=C0103
    def _modify_filename(self, n):
        root, suffix = os.path.splitext(self.path)
        path = '{}_({}){}'.format(
            root,
            n,
            suffix
        )
        return path


def get_pixel_file_paths(directory):
    """
    Gets a list of all valid pixel JV data file paths contained in directory

    Parameters
    ----------
    directory : str
        the directory to scan

    Returns
    ----------
    list
        list of pixel JV data file paths

    """
    pixel_files_paths = []
    for a_file in os.listdir(directory):
        # if file in directory is a text file that is not the char file
        if (os.path.isfile(os.path.join(directory, a_file)) and
                a_file.endswith('.txt') and 'char' not in a_file):
            path = os.path.join(directory, a_file)
            with open(path) as pixel_file:
                # if file contains header indicating proper JV file
                try:
                    if 'Bias (V)' in pixel_file.next():
                        pixel_files_paths.append(path)
                except StopIteration:
                    pass
    return pixel_files_paths


def extract_data(pixel_files_paths, minimum_voc):
    """
    Processes each JV pixel file in pixel_files_paths and creates a new
    jvtool.ss_device.Pixel object for each file. JV pixel files with a Voc
    less than minimum_voc will be ignored.

    Parameters
    ----------
    pixel_files_paths : str
        list of valid JV data pixel files
    minimum_voc : float
        minimum_voc allowed for a pixel to be considered

    Returns
    ----------
    list
        list of Pixel objects corresponding to each JV pixel file
    """
    pixel_list = []
    for file_path in pixel_files_paths:
        with open(file_path) as pixel_file:
            directory, filename = os.path.split(pixel_file.name)
            name = filename.split('.')[0]
            # noinspection PyTypeChecker
            bias, current_density, current = np.loadtxt(
                pixel_file,
                dtype='f8,f8,f8',
                skiprows=1,
                usecols=(0, 1, 2),
                delimiter='\t',
                unpack=True)

            # create JVCurve object from data
            jv_curve = jv_calculations.JVCurve(
                bias,
                current,
                current_density,
                minimum_voc
            )

            # create Pixel object from data
            a_pixel = ss_device.Pixel(
                name,
                directory,
                jv_curve,
            )
            pixel_list.append(a_pixel)
    return pixel_list


def prompt_overwrite(file_type):
    """
    Prompts user if they want to overwrite files of type file_type

    Parameters
    ----------
    file_type : str
        the file_type that the user is prompted for overwrite

    Returns
    ----------
    bool
        True if overwrite of file_type is desired, False otherwise
    """
    print ('Do you want to overwrite existing %s files if they exist?'
           % file_type)
    overwrite = raw_input('(y/n) > ')
    return overwrite.lower().startswith('y')



