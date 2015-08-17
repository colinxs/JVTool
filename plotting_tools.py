

__author__ = 'Colin Summers'
__copyright__ = 'Copyright 2015, Ginger Lab'
__maintainer__ = 'Colin Summers'
__email__ = 'colinxs@uw.edu'
__status__ = 'Development'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(new_file, x_data, y_data, bounds, x_label='', y_label=''):
    """
    Saves a plot as 'new_file.name' on given bounds or auto-ranged
    bounds if none given.

    Parameters
    ----------
    new_file : File object
        file handle of plotting output file
    x_data : list
        x_data to be plotted against
    y_data : list
        y_data to be plotted
    bounds : tuple
        bounds to be plotted against (min_x, max_x, min_y, max_y)    
   """
    if bounds:
        min_x, max_x, min_y, max_y = bounds
    else:
        min_x = x_data[0]
        max_x = x_data[-1]
        y_data_array = np.asarray(y_data)
        min_y = np.amin(y_data_array)
        max_y = np.amax(y_data_array)
        
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data)
    ax.set_xlabel(x_label, position=(0.5, 0))
    ax.set_ylabel(y_label)
    ax.axis([min_x, max_x, min_y, max_y])
    # ax.set_aspect('equal')
    ax.grid(True, which='both')
    # set the x-spine (see below for more info on `set_position`)
    ax.spines['left'].set_position('zero')
    # turn off the right spine/ticks
    ax.spines['right'].set_color('none')
    ax.yaxis.tick_left()
    # set the y-spine
    ax.spines['bottom'].set_position('zero')
    # turn off the top spine/ticks
    ax.spines['top'].set_color('none')
    ax.xaxis.tick_bottom()
    fig.savefig(new_file, format='png')
    print '%s saved successfully!' % new_file.name
    plt.close(fig)


def get_bounds():
    """Gets desired plotting bounds from user, returns None if no bounds 
    
    Returns
    ----------
    tuple
        (min_x, max_x, min_y, max_y)
    """ 
    print 'Do you want to set bounds for JV data plot (else auto-range)?'
    bounds_answer = raw_input('(y/n) > ')
    if bounds_answer.lower().startswith('y'):
        print 'What bounds do you want to plot your JV curve on?'
        min_x = int(raw_input('min X > '))
        max_x = int(raw_input('max X > '))
        min_y = int(raw_input('min Y > '))
        max_y = int(raw_input('max Y > '))
        return min_x, max_x, min_y, max_y
    else:
        return None
