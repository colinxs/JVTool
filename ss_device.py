

__author__ = 'Colin Summers'
__copyright__ = 'Copyright 2015, Ginger Lab'
__maintainer__ = 'Colin Summers'
__email__ = 'colinxs@uw.edu'
__status__ = 'Development'

import statistics
import os
import matplotlib
matplotlib.use('Agg')
from collections import OrderedDict
import numpy as np
from scipy.interpolate import UnivariateSpline

class Pixel(object):
    """
    The Pixel class represents a set of JV data for an individual pixel
    of a photovoltaic device.

    Attributes
    ----------
        directory : str
            the directory containing`this pixel's JV data
        name : str
            the fillname of this pixel's JV data
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
    def __init__(self, 
                 name, 
                 directory, 
                 bias_data, 
                 current_data, 
                 current_density_data,
                 V_to_J,
                 V_to_I,
                 minimum_voc
    ):
        """ Initializes an instance of Pixel object"""
        self.directory = directory
        self.name = name
        self.current_density = current_density_data.tolist()
        self.current = current_data.tolist()
        self.bias = bias_data.tolist()
        self.min_Voc = minimum_voc
        self.V_to_J = V_to_J
        self.V_to_I = V_to_I
        self.power_curve = self.create_power_curve()
        self.Voc = self.calc_Voc()
        self.Jsc = self.calc_Jsc()
        self.Isc = self.calc_Isc()
        self.FF = self.calc_FF()
        self.PCE = self.calc_PCE()
        self.area = self.calc_area()
        
        

    def calc_area(self):
        """Return the area of this pixel"""
        if self.Voc != None:
            return round(self.Isc / self.Jsc * 1000, 3)
        else:
            return None

    def create_power_curve(self):
        """Return the power curve of this pixel"""
        power_curve = []
        for i in range(0, len(self.bias)):
            power_curve.append(self.bias[i] * self.current_density[i])
        return power_curve

    def _check_index(self, index):
        """
        Checks if index is within the bounds of this pixel's data

        Parameters
        ----------
            index : int 
                the index to be checked for validity

        Return:
        ----------
            True if index is within the bounds of this pixels domain of
            valid indices, False otherwise
        """
        return (index > 0) and (index < len(self.bias))

    def calc_Voc(self):
        """
        Calculate and return the Voc of this pixel.
        
        Returns
        ----------
            None if no Voc exists meaning that this pixel is invalid
        """
        zero_crossings = statistics.find_zero_crossings(self.current_density)
        # if a zero crossing in JV curve exists
        if len(zero_crossings) == 1:
            # index of nearest value to Voc
            zero_index = zero_crossings[0]

            # sets lower and upper limits of subrange of data to fit spline
            number_of_data_points = len(self.bias)
            sub_range = number_of_data_points / 10
            lower_limit_range = zero_index - sub_range
            upper_limit_range = zero_index + sub_range
 
           # sets lower_limit_range to 0 if outside of data range
            if not self._check_index(lower_limit_range):
                lower_limit_range = 0
            # sets upper_limit_range to end of data list if outside data range
            if not self._check_index(upper_limit_range):
                upper_limit_range = len(self.bias) - 1

            # Takes subrange slice of self.bias and self.current_density
            # from lower_limit_range to upper_limit_range
            subregion_of_bias = self.bias[lower_limit_range:upper_limit_range]
            subregion_of_current_density = (
                self.current_density[lower_limit_range:upper_limit_range])

            # fit univariate spline with no smoothing to region surronding Voc
            # and return largest root
            current_density_spline = UnivariateSpline(
                subregion_of_bias,
                subregion_of_current_density,
                k=3,
                s=0)
            current_density_spline_roots = current_density_spline.roots()
            # Voc at end of list, corresponding to largest Voc found
            Voc = current_density_spline_roots[-1]
            if Voc > self.min_Voc:
                return Voc
            else:
                return None
        else:
            return None

    def calc_Jsc(self):
        """
        Calculate and return Jsc of this pixel.
        
        Returns
        ----------
            Jsc of pixel, None if no Voc exists meaning that this pixel is invalid.
        """
        # Look up current density at 0 applied bias
        if self.Voc != None:
            return abs(self.V_to_J[0])
        else:
            return None

    def calc_Isc(self):
        """
        Calculate and return Isc of this pixel.
        
        Returns
        ----------
            Isc of pixel, None if no Voc exists meaning that this pixel is invalid.
        """
        if self.Voc != None:
            return abs(self.V_to_I[0])
        else:
            return None

    def calc_PCE(self):
        """
        Calculate and return PCE of this pixel.
        
        Returns
        ----------
            PCE of pixel, None if no Voc exists meaning that this pixel is invalid.
        """
        if self.Voc != None:
            return self.Voc * self.Jsc * self.FF
        else:
            return None

    def calc_FF(self):
        """
        Calculate and return Fill Factor of this pixel.
        
        Return
        ----------
            Fill Factor of pixel, None if no Voc exists meaning that this pixel is invalid
        """
        if self.Voc != None:
            # zero crossings of power curve, ideally should only be one value
            zero_crossings_of_power = statistics.find_zero_crossings(
                self.power_curve)

            # set lower_limit_range to index corresponding to 0 power
            lower_limit_range = self.bias.index(0)

            # sets upper_limit_range to index of zero crossing if exists,
            # otherwise set to end of data list
            upper_limit_range = len(self.bias) - 1
            if len(zero_crossings_of_power) == 1:
                upper_limit_range = zero_crossings_of_power[-1]

            # fit univariate spline with no smoothing to subregion of power
            # curve where maximum power occurs
            subregion_of_bias = self.bias[lower_limit_range:upper_limit_range]
            subregion_of_power_curve = self.power_curve[lower_limit_range:
                                                        upper_limit_range]
            power_curve_spline = UnivariateSpline(subregion_of_bias,
                                                  subregion_of_power_curve,
                                                  k=4,
                                                  s=0)
            power_curve_spline_deriv = power_curve_spline.derivative()

            # Find maximum power by finding critical points of power curve fit
            # and testing each value
            power_curve_spline_deriv_roots = power_curve_spline_deriv.roots()
            potential_power = (
                power_curve_spline(power_curve_spline_deriv_roots))
            idx_root_of_max_power = np.argmin(np.asarray(potential_power))

            # calcluate fill factor
            actual_max_pwr = potential_power[idx_root_of_max_power]
            theoretical_max_pwr = self.Voc * self.Jsc
            fill_factor = abs(actual_max_pwr / theoretical_max_pwr)
            return fill_factor
        else:
            return None

        
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

    def calc_stat_FF(self):
        """
        Calculates Fill Factor statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Fill Factors for this device.
        """
        list_of_FF = []
        for pixel in self.pixel_list: 
            FF = pixel.FF
            if FF != None:
                list_of_FF.append(FF)
        return (
            np.mean(list_of_FF), 
            np.std(list_of_FF), 
            statistics.q_test(list_of_FF),
            np.median(list_of_FF))

    def calc_stat_PCE(self):
        """
        Calculates PCE statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, and median)
            of Power Conversion Efficiency for this device.
        """
        list_of_PCE = []
        for pixel in self.pixel_list:
            PCE = pixel.PCE
            if PCE != None:
                list_of_PCE.append(PCE)
        return (np.mean(list_of_PCE), 
                np.std(list_of_PCE), 
                statistics.q_test(list_of_PCE),
                np.median(list_of_PCE))

    def calc_stat_Jsc(self):
        """
        Calculates Jsc statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Jsc for this device.
        """
        list_of_Jsc = []
        for pixel in self.pixel_list:
            Jsc = pixel.Jsc
            if Jsc != None:
                list_of_Jsc.append(Jsc)
        return (np.mean(list_of_Jsc), 
                np.std(list_of_Jsc), 
                statistics.q_test(list_of_Jsc),
                np.median(list_of_Jsc))

    def calc_stat_Voc(self):
        """
        Calculates Voc statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Voc's for this device.
        """
        list_of_Voc = []
        for pixel in self.pixel_list:
            Voc = pixel.Voc
            if Voc != None:
                list_of_Voc.append(Voc)
        return (np.mean(list_of_Voc), 
                np.std(list_of_Voc), 
                statistics.q_test(list_of_Voc),
                np.median(list_of_Voc))

    def calc_stat_Isc(self):
        """
        Calculates Isc statistics (mean, median, Q-Test, Std. Dev)
        
        Returns
        ----------
        Tuple 
            (mean, standard deviation, Q_Test outliers, median)
            of Isc's for this device.
        """
        list_of_Isc = []
        for pixel in self.pixel_list:
            Isc = pixel.Isc
            if Isc != None:
                list_of_Isc.append(Isc)
        return (np.mean(list_of_Isc), 
                np.std(list_of_Isc), 
                statistics.q_test(list_of_Isc),
                np.median(list_of_Isc))