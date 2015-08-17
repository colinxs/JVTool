

import statistics
import numpy as np
from scipy.interpolate import UnivariateSpline


# noinspection PyPep8Naming
class JVCurve(object):
    """
    The JVCurve class represents a set of JV data

    Attributes
    ----------
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
            this JV curve's short circuit current
        Jsc : float
            this JV curve's short circuit current density
        Voc : float
            this JV curve's open circuit voltage
        FF : float
            this JV curve's fill factor
        PCE : float
            this JV curve's power conversion efficiency
        area : float
            this JV curve's area in cm^2
        power_curve : float
            this pixels power density curve defined as J*V
    """
    def __init__(
        self,
        bias_data,
        current_data,
        current_density_data,
        minimum_voc
    ):
        """ Initializes an instance of Pixel object"""
        self.current_density = current_density_data.tolist()
        self.current = current_data.tolist()
        self.bias = bias_data.tolist()
        self.min_Voc = minimum_voc
        self.V_to_J = dict(zip(bias_data, current_density_data))
        self.V_to_I = dict(zip(bias_data, current_data))
        self.power_curve = self.create_power_curve()
        self.Voc = self.calc_Voc()
        self.Jsc = self.calc_Jsc()
        self.Isc = self.calc_Isc()
        self.FF = self.calc_FF()
        self.PCE = self.calc_PCE()
        self.area = self.calc_area()

    def calc_area(self):
        """Return the area of this pixel"""
        if self.Voc is not None:
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

    # noinspection PyPep8Naming
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

            # fit univariate spline with no smoothing to region surrounding Voc
            # and return largest root
            current_density_spline = UnivariateSpline(
                subregion_of_bias,
                subregion_of_current_density,
                k=3,
                s=0)
            current_density_spline_roots = current_density_spline.roots()
            # Voc at end of list, corresponding to largest Voc found
            # noinspection PyPep8Naming
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
        if self.Voc is not None:
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
        if self.Voc is not None:
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
        if self.Voc is not None:
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
        if self.Voc is not None:
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

            # calculate fill factor
            actual_max_pwr = potential_power[idx_root_of_max_power]
            theoretical_max_pwr = self.Voc * self.Jsc
            fill_factor = abs(actual_max_pwr / theoretical_max_pwr)
            return fill_factor
        else:
            return None
