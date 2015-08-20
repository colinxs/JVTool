

__author__ = 'Colin Summers'
__copyright__ = 'Copyright 2015, Ginger Lab'
__maintainer__ = 'Colin Summers'
__email__ = 'colinxs@uw.edu'
__status__ = 'Development'

import io_handling
import ss_device
import os
import plotting_tools


def main():
    
    # get charfile overwrite preference
    print ('Data file will be named as pixel_filename.txt where'
           ' pixel_filename is the filename of the corresponding pixel\'s'
           ' JV data .txt file.')
    charfile_overwrite = io_handling.prompt_overwrite('device data')
    
    # get minimum tolerable Voc
    print ('What is the minimum allowed Voc values? This is'
           ' used to eliminate outliers/dead pixels from your data.')
    minimum_voc = float(raw_input('min? >'))
    
    # save JV plots, if desired
    print 'Do you want images?'
    plot_data = raw_input('(y/n) > ').lower().startswith('y')

    if plot_data:
        # get plot overwrite preference
        print (
            'Image files will be named as pixel_filename.png where'
            ' pixel_filename is the filename of the corresponding pixel\'s'
            ' JV data .txt file.')
        plot_overwrite = io_handling.prompt_overwrite('image files')
        # get desired bounds if any for saving JV plots
        plot_bounds = plotting_tools.get_bounds()
    
    # continue to prompt user for directory paths until undesired
    continue_processing = True
    while continue_processing:
        # get directory path
        directory_path = io_handling.get_dir_path()
        print '\n'
        
        # 
        if plot_data:
            _process_data(directory_path=directory_path,
                         minimum_voc=minimum_voc,
                         charfile_overwrite=charfile_overwrite,
                         plot_data=plot_data,
                         plot_overwrite=plot_overwrite,
                         plot_bounds=plot_bounds)
        else:
            _process_data(directory_path=directory_path,
                         minimum_voc=minimum_voc,
                         charfile_overwrite=charfile_overwrite)

        print 'Do you have another device?'
        continue_answer = raw_input('(y/n) > ').lower().startswith('y')
        print '\n'
        if not continue_answer:
            continue_processing = False

    print 'Have a great day!'
    
def _process_data(directory_path,
                 minimum_voc,
                 plot_data=False,
                 charfile_overwrite=False,
                 plot_overwrite=False,
                 plot_bounds=None):
    """Manages various file process tasks

    Parameters
    ----------
    directory_path : str
        path to folder to be processed
    minimum_voc : int
        minimum allowable Voc, used to a simple way to eliminate dead pixels
    plot_data : bool
        true if plot of data desired, false otherwise
    charfile_overwrite : bool
        true if overwrite of device charfile is desired, false otherwise
    plot_overwrite : bool
        true if overwrite of device charfile is desired, false otherwise
    plot_bounds : tuple
        tuple of (min_x, max_x, min_y, max_y) bounds for plotting
    """
    pixel_file_paths = io_handling.get_pixel_file_paths(directory_path)
    pixel_list = io_handling.extract_data(pixel_file_paths, minimum_voc)
    device = ss_device.Device(pixel_list, directory_path)
    
    # save device parameters
    save_device_parameters(device, charfile_overwrite)
    print '\n'
    
    if plot_data:
        save_plot(device, plot_overwrite, plot_bounds)
        print '\n'
    


def save_device_parameters(device, overwrite):
    """Saves this device's parameters in a file named device_name.txt

    Parameters
    ----------
    device : Device object
        the current device being saved
    overwrite : bool
        true if overwrite of device charfile desired, false otherwise
    """
    filename = device.device_name + '.txt'
    file_path = os.path.join(device.directory, filename)
    with io_handling.HandleFileSave(file_path, overwrite) as new_file:
        _save_device_parameters_helper(device,
                                       new_file)


def _save_device_parameters_helper(device, new_file):
    """
    Formats and writes device parameters to new_file

    Parameters
    ----------
    device : Device object
        the current device being saved
    new_file : File object
        file handle of parameter save file
    """
    # file header
    new_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
        'Pixel Name',
        'Voc (V)',
        'Isc (A)',
        'Area (cm^2)',
        'Jsc (mA/cm^2)',
        'Fill Factor',
        'PCE',
        'Rs',
        'Rsh'))
    # individual pixel parameters
    for pixel in device.pixel_list:
        if pixel.jv_curve.Voc is not None:
            # individual pixel parameters
            new_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                pixel.name,
                pixel.jv_curve.Voc,
                pixel.jv_curve.Isc,
                pixel.jv_curve.area,
                pixel.jv_curve.Jsc,
                pixel.jv_curve.FF,
                pixel.jv_curve.PCE,
                pixel.jv_curve.Rs,
                pixel.jv_curve.Rsh))
    # device parameter mean
    new_file.write(
        'Averages:\t{}\t{}\t\t{}\t{}\t{}\t{}\t{}\n'.format(
            device.mean_Voc,
            device.mean_Isc,
            device.mean_Jsc,
            device.mean_FF,
            device.mean_PCE,
            device.mean_Rs,
            device.mean_Rsh))
    # device parameter standard deviation
    new_file.write(
        'Std. Dev:\t{}\t{}\t\t{}\t{}\t{}\t{}\t{}\n'.format(
            device.std_Voc,
            device.std_Isc,
            device.std_Jsc,
            device.std_FF,
            device.std_PCE,
            device.std_Rs,
            device.std_Rsh))
    # device parameter median
    new_file.write(
        'Median:\t{}\t{}\t\t{}\t{}\t{}\t{}\t{}\n'.format(
            device.median_Voc,
            device.median_Isc,
            device.median_Jsc,
            device.median_FF,
            device.median_PCE,
            device.median_Rs,
            device.median_Rsh))
    # device parameter Q-Test Outliers
    new_file.write(
        'Q-Test Outliers:\t{}\t{}\t\t{}\t{}\t{}\t{}\t{}\n'.format(
            device.outliers_Voc,
            device.outliers_Isc,
            device.outliers_Jsc,
            device.outliers_FF,
            device.outliers_PCE,
            device.outliers_Rs,
            device.outliers_Rsh))
    print '\'{}\' saved successfully!'.format(new_file.name)


def save_plot(device, overwrite, bounds):
    """Saves JV plots for each Pixel in this Device

    Parameters
    ----------
    device : Device object
        the current device being considered
    bounds : tuple
        tuple of (min_x, max_x, min_y, max_y) bounds for plotting
    overwrite : bool
        true if overwrite of device charfile is desired, false otherwise
    """
    for pixel in device.pixel_list:
        image_name = '{}.{}'.format(pixel.name, 'png')
        image_path = os.path.join(device.directory, image_name)
        with io_handling.HandleFileSave(image_path, overwrite) as new_file:
            plotting_tools.plot(new_file,
                                pixel.jv_curve.bias,
                                pixel.jv_curve.current_density,
                                bounds)

if __name__ == '__main__':
    main()
