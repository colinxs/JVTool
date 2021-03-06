

__author__ = 'Colin Summers'
__copyright__ = 'Copyright 2015, Ginger Lab'
__maintainer__ = 'Colin Summers'
__email__ = 'colinxs@uw.edu'
__status__ = 'Development'

import src.statistics
import os
from collections import OrderedDict
import numpy as np


class Pixel(object):
    """
    The Pixel class represents a set of JV data for an individual pixel
    of a photovoltaic device.

    Attributes
    ----------
        directory : str
            the directory containing`this pixel's JV data
        name : str
            the filename of this pixel's JV data
        V_to_J : OrderedDict
            a dict of Bias-->Current Density whose values are represented
            as strings
        V_to_I : OrderedDict
            a dict of Bias-->Current whose values are represented as
            strings
        current_density_data : list
            float values of current density data
        current_data: list
            float values of current data
        bias : float
            values of bias data
        min_voc : float
            minimum tolerable pixel Voc to be considered valid
        Isc : float
            this pixel's short circuit current
        Jsc : float
            this pixel's short circuit current density
        Voc : float
            this pixel's open circuit voltage
        FF : float
            this pixel's fill factor
        PCE : float
            this pixel's power conversion efficiency
        area : float
            this pixel's area in cm^2
        power_curve : float
            this pixels power density curve defined as J*V
    """
    def __init__(
        self,
        name,
        directory,
        jv_curve
    ):
        """ Initializes an instance of Pixel object"""
        self.directory = directory
        self.name = name
        self.jv_curve = jv_curve


# noinspection PyPep8Naming
class Device(object):
    """
    The Device class represents a composition of Pixel objects.
    
    Attributes
    ----------
        directory : str
            directory of this device's JV data.
        name_to_pixel : dict
            map of pixel_name --> Pixel object
        device_name : str
            name of this device corresponding to name of directory
            holding this device's JV data
        mean_XX : float
            mean of XX (Fill Factor, Isc, Jsc, Voc, or PCE)
        std_XX : float
            standard deviation of XX (Fill Factor, Isc, Jsc, Voc, or PCE)
        outliers_XX : list
            Dixon's Q_Test outliers of of XX (Fill Factor, Isc, Jsc, Voc, or PCE)
        median_XX : float
            median of XX (Fill Factor, Isc, Jsc, Voc, or PCE)
    """

    def __init__(self, pixel_list, directory):
        self.directory = directory
        self.name_to_pixel = OrderedDict()
        self.device_name = os.path.basename(directory)
        self.pixel_list = pixel_list
        self.mean_FF, self.std_FF, self.outliers_FF, self.median_FF = self.calc_stat_FF()
        self.mean_Isc, self.std_Isc, self.outliers_Isc, self.median_Isc = self.calc_stat_Isc()
        self.mean_Jsc, self.std_Jsc, self.outliers_Jsc, self.median_Jsc = self.calc_stat_Jsc()
        self.mean_Voc, self.std_Voc, self.outliers_Voc, self.median_Voc = self.calc_stat_Voc()
        self.mean_PCE, self.std_PCE, self.outliers_PCE, self.median_PCE = self.calc_stat_PCE()
        self.mean_Rs, self.std_Rs, self.outliers_Rs, self.median_Rs = self.calc_stat_Rs()
        self.mean_Rsh, self.std_Rsh, self.outliers_Rsh, self.median_Rsh = self.calc_stat_Rsh()

    def calc_stat_FF(self):
        """
        Calculates Fill Factor src.statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Fill Factors for this device.
        """
        list_of_FF = []
        for pixel in self.pixel_list: 
            FF = pixel.jv_curve.FF
            if FF is not None:
                list_of_FF.append(FF)
        if len(list_of_FF) > 0:
            return (np.mean(list_of_FF),
                    np.std(list_of_FF),
                    src.statistics.q_test(list_of_FF),
                    np.median(list_of_FF))
        else:
            return None, None, None, None

    def calc_stat_PCE(self):
        """
        Calculates PCE src.statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, and median)
            of Power Conversion Efficiency for this device.
        """
        list_of_PCE = []
        for pixel in self.pixel_list:
            PCE = pixel.jv_curve.PCE
            if PCE is not None:
                list_of_PCE.append(PCE)
        if len(list_of_PCE) > 0:
            return (np.mean(list_of_PCE),
                    np.std(list_of_PCE),
                    src.statistics.q_test(list_of_PCE),
                    np.median(list_of_PCE))
        else:
            return None, None, None, None

    def calc_stat_Jsc(self):
        """
        Calculates Jsc src.statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Jsc for this device.
        """
        list_of_Jsc = []
        for pixel in self.pixel_list:
            Jsc = pixel.jv_curve.Jsc
            if Jsc is not None:
                list_of_Jsc.append(Jsc)
        if len(list_of_Jsc) > 0:
            return (np.mean(list_of_Jsc),
                    np.std(list_of_Jsc),
                    src.statistics.q_test(list_of_Jsc),
                    np.median(list_of_Jsc))
        else:
            return None, None, None, None

    def calc_stat_Voc(self):
        """
        Calculates Voc src.statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Voc's for this device.
        """
        list_of_Voc = []
        for pixel in self.pixel_list:
            Voc = pixel.jv_curve.Voc
            if Voc is not None:
                list_of_Voc.append(Voc)
        if len(list_of_Voc) > 0:
            return (np.mean(list_of_Voc),
                    np.std(list_of_Voc),
                    src.statistics.q_test(list_of_Voc),
                    np.median(list_of_Voc))
        else:
            return None, None, None, None


    def calc_stat_Isc(self):
        """
        Calculates Isc src.statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Isc's for this device.
        """
        list_of_Isc = []
        for pixel in self.pixel_list:
            Isc = pixel.jv_curve.Isc
            if Isc is not None:
                list_of_Isc.append(Isc)
        if len(list_of_Isc) > 0:
            return (np.mean(list_of_Isc),
                    np.std(list_of_Isc),
                    src.statistics.q_test(list_of_Isc),
                    np.median(list_of_Isc))
        else:
            return None, None, None, None

    def calc_stat_Rs(self):
        """
        Calculates series resistance src.statistics (mean, median, Q-Test, Std. Dev)

        Returns
        ----------
        Tuple
            (mean, standard deviation, Q_Test outliers, median)
            of series resistances's for this device.
        """
        list_of_Rs = []
        for pixel in self.pixel_list:
            Rs = pixel.jv_curve.Rs
            if Rs is not None:
                list_of_Rs.append(Rs)
        if len(list_of_Rs) > 0:
            return (np.mean(list_of_Rs),
                    np.std(list_of_Rs),
                    src.statistics.q_test(list_of_Rs),
                    np.median(list_of_Rs))
        else:
            return None, None, None, None

    def calc_stat_Rsh(self):
        """
        Calculates shunt resistance src.statistics (mean, median, Q-Test, Std. Dev)

        Returns
        ----------
        Tuple
            (mean, standard deviation, Q_Test outliers, median)
            of shunt resistances's for this device.
        """
        list_of_Rsh = []
        for pixel in self.pixel_list:
            Rsh = pixel.jv_curve.Rsh
            if Rsh is not None:
                list_of_Rsh.append(Rsh)
        if len(list_of_Rsh) > 0:
            return (np.mean(list_of_Rsh),
                    np.std(list_of_Rsh),
                    src.statistics.q_test(list_of_Rsh),
                    np.median(list_of_Rsh))
        else:
            return None, None, None, None
