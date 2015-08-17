

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

    continue_processing = True
    while continue_processing:
        # get directory path
        directory_path = io_handling.get_dir_path()
        # directory_path = 'C:\\testfiles'
        print '\n'
        print ('What is the minimum allowed Voc values? This is'
               ' used to eliminate outliers/dead pixels from your data.')

        # get minimum tolerable Voc
        minimum_voc = float(raw_input('min? >'))
        print '\n'
        pixel_file_paths = io_handling.get_pixel_file_paths(directory_path)
        pixel_list = io_handling.extract_data(pixel_file_paths, minimum_voc)
        device = ss_device.Device(pixel_list, directory_path)

        # save JV plots, if desired
        print 'Do you want images?'
        image_answer = raw_input('(y/n) > ')
        print '\n'
        if image_answer.lower().startswith('y'):
            save_plot(device)
        print '\n'

        # save device parameters
        save_device_parameters(device)
        print '\n'
        print 'Do you have another device?'
        continue_answer = raw_input('(y/n) > ')
        if not continue_answer.lower().startswith('y'):
            continue_processing = False
        print '\n'

    print 'Have a great day!'


def save_device_parameters(device):
    """Saves this device's parameters in a file named device_name.txt

    Parameters
    ----------
    device : Device object
        the current device being saved
    """
    print ('Data file will be named as pixel_filename.txt where'
           ' pixel_filename is the filename of the corresponding pixel\'s'
           ' JV data .txt file.')
    filename = device.device_name + '.txt'
    file_path = os.path.join(device.directory, filename)
    overwrite = io_handling.prompt_overwrite('device data')
    with io_handling.HandleFileSave(file_path, overwrite) as new_file:
        _save_device_parameters_helper(
            device,
            new_file,
        )


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
    new_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
        'Pixel Name',
        'Voc (V)',
        'Isc (A)',
        'Area (cm^2)',
        'Jsc (mA/cm^2)',
        'Fill Factor',
        'PCE'))
    # individual pixel parameters
    for pixel in device.pixel_list:
        if pixel.jv_curve.Voc is not None:
            # individual pixel parameters
            new_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
                pixel.name,
                pixel.jv_curve.Voc,
                pixel.jv_curve.Isc,
                pixel.jv_curve.area,
                pixel.jv_curve.Jsc,
                pixel.jv_curve.FF,
                pixel.jv_curve.PCE))
    # device parameter mean
    new_file.write(
        'Averages:\t{}\t{}\t\t{}\t{}\t{}\n'.format(
            device.mean_Voc,
            device.mean_Isc,
            device.mean_Jsc,
            device.mean_FF,
            device.mean_PCE))
    # device parameter standard deviation
    new_file.write(
        'Std. Dev:\t{}\t{}\t\t{}\t{}\t{}\n'.format(
            device.std_Voc,
            device.std_Isc,
            device.std_Jsc,
            device.std_FF,
            device.std_PCE))
    # device parameter median
    new_file.write(
        'Median:\t{}\t{}\t\t{}\t{}\t{}\n'.format(
            device.median_Voc,
            device.median_Isc,
            device.median_Jsc,
            device.median_FF,
            device.median_PCE))
    # device parameter median
    new_file.write(
        'Q-Test Outliers:\t{}\t{}\t\t{}\t{}\t{}\n'.format(
            device.outliers_Voc,
            device.outliers_Isc,
            device.outliers_Jsc,
            device.outliers_FF,
            device.outliers_PCE))
    print '\'{}\' saved successfully!'.format(new_file.name)


def save_plot(device):
    """Saves JV plots for each Pixel in this Device

    Parameters
    ----------
    device : Device object
        the current device being considered
    """
    print (
        'Image files will be named as pixel_filename.png where'
        ' pixel_filename is the filename of the corresponding pixel\'s'
        ' JV data .txt file.')
    # get boolean flag for overwrite permission
    overwrite = io_handling.prompt_overwrite('image files')
    print '\n'
    # get desired bounds if any for saving JV plots
    bounds = plotting_tools.get_bounds()
    print '\n'
    for pixel in device.pixel_list:
        image_name = '{}.{}'.format(pixel.name, 'png')
        image_path = os.path.join(device.directory, image_name)
        with io_handling.HandleFileSave(image_path, overwrite) as new_file:
            plotting_tools.plot(
                new_file,
                pixel.jv_curve.bias_data,
                pixel.jv_curve.current_density_data,
                bounds
            )

if __name__ == '__main__':
    main()
