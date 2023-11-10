import logging
import os

import matplotlib.pyplot as plt
import yaml
from datetime import datetime
import math
import h5py
import numpy as np
from LightPipes import um, mm

def configure_logging(result_directory, log_directory="logs"):
    log_directory = os.path.join(result_directory, log_directory)
    os.makedirs(log_directory, exist_ok=True)

    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    log_file_name = f"experiment_{timestamp}.log"

    file_handler = logging.FileHandler(os.path.join(log_directory, log_file_name))
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

def initialize_directory(config):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_directory = os.path.join(config["results directory"], config["simulation name"], timestamp)
    os.makedirs(result_directory, exist_ok=True)
    return result_directory

def load_yaml_config(file_path):
    """
    Load a YAML configuration file.

    :param file_path: Path to the YAML file
    :return: A dictionary containing the configuration data
    """
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

def load_all_configs():
    """
    Load all YAML configuration files in a directory.

    :param config_directory: Path to the directory containing the YAML files
    :return: A dictionary containing the configuration data
    """
    config_directory = "./beamshapy_gui/config/"
    configs = {}
    for file_name in os.listdir(config_directory):
        if file_name.endswith(".yml"):
            config_name = os.path.splitext(file_name)[0]
            configs[config_name] = load_yaml_config(os.path.join(config_directory, file_name))
    return configs

def save_frames_to_h5(frames_data, result_directory, file_name="frames.h5"):
    """
    Save a list of images of timestamps (frames) to an h5 file.

    :param frames_data: A tuple containing the list of frames and the list of frame times
    :param result_directory: Directory where the h5 file will be saved
    :param file_name: Name of the h5 file (default: "frames.h5")
    """
    frames_list, frame_times = frames_data

    # Ensure the result_directory exists
    os.makedirs(result_directory, exist_ok=True)

    # Create an h5 file in the specified directory with the given file name
    with h5py.File(os.path.join(result_directory, file_name), "w") as h5_file:
        # Create a dataset for the frames
        frames_dataset = h5_file.create_dataset(
            "frames",
            shape=(len(frames_list), *frames_list[0].shape),
            dtype=np.float32
        )

        # Create a dataset for the frame times
        frame_times_dataset = h5_file.create_dataset(
            "frame_times",
            shape=(len(frame_times),),
            dtype=np.float64
        )

        # Save each frame and frame time to the datasets
        for i, (frame, frame_time) in enumerate(zip(frames_list, frame_times)):
            frames_dataset[i] = frame
            frame_times_dataset[i] = frame_time

def undersample_grid(grid, target_size=40):
    factor = grid.shape[0] // target_size
    if factor == 0:
        return grid[::1,::1]
    return grid[::factor,::factor]




def normalize(mask, min_value, max_value):
    # Normalize the mask to the range [min_value, max_value]
    mask_min = mask.min()
    mask_max = mask.max()
    return min_value + (max_value - min_value) * (mask - mask_min) / (mask_max - mask_min)


def translate(mask,value):
    mask = np.roll(mask, value, axis=1)
    return mask

def save_generated_fields(beam_shaper, modulated_input_field, fourier_plane_field, fourier_filtered_field, output_field,
                          results_directory):


    # Save the modulated input field
    os.makedirs(results_directory, exist_ok=True)
    if modulated_input_field is not None:
        modulated_input_field = modulated_input_field

        # Calculate the other two arrays
        intensity = np.abs(modulated_input_field.field) ** 2
        phase = np.angle(modulated_input_field.field)
        # Save the arrays in an H5 file
        file_path = os.path.join(results_directory, 'modulated_input_field.h5')
        counter = 0
        while os.path.exists(f'{file_path}'):
            counter += 1
            file_path = os.path.join(results_directory, f'modulated_input_field{counter}.h5')

        with h5py.File(file_path, 'w') as f:
            f.create_dataset('intensity', data=intensity)
            f.create_dataset('phase', data=phase)
            f.create_dataset('x_vector_mm', data=beam_shaper.x_array_out / mm)

        print("modulated_input_field data saved !")
    else:
        print("No modulated_input_field data to save")

    if fourier_plane_field is not None:
        fourier_plane_field = fourier_plane_field

        # Calculate the other two arrays
        intensity = np.abs(fourier_plane_field.field) ** 2
        phase = np.angle(fourier_plane_field.field)
        # Save the arrays in an H5 file
        file_path = os.path.join(results_directory, 'fourier_plane_field.h5')
        counter = 0
        while os.path.exists(f'{file_path}'):
            counter += 1
            file_path = os.path.join(results_directory, f'fourier_plane_field{counter}.h5')

        with h5py.File(file_path, 'w') as f:
            f.create_dataset('intensity', data=intensity)
            f.create_dataset('phase', data=phase)
            f.create_dataset('x_vector_mm', data=beam_shaper.x_array_out / mm)

        print("Fourier plane field data saved !")
    else:
        print("No Fourier plane field data to save")

    if fourier_filtered_field is not None:
        fourier_filtered_field = fourier_filtered_field

        # Calculate the other two arrays
        intensity = np.abs(fourier_filtered_field.field) ** 2
        phase = np.angle(fourier_filtered_field.field)
        # Save the arrays in an H5 file
        file_path = os.path.join(results_directory, 'fourier_filtered_field.h5')
        counter = 0
        while os.path.exists(f'{file_path}'):
            counter += 1
            file_path = os.path.join(results_directory, f'fourier_filtered_field{counter}.h5')

        with h5py.File(file_path, 'w') as f:
            f.create_dataset('intensity', data=intensity)
            f.create_dataset('phase', data=phase)
            f.create_dataset('x_vector_mm', data=beam_shaper.x_array_out / mm)

        print("Fourier filtered field saved !")
    else:
        print("No fFourier filtered field to save")

    if output_field is not None:
        output_field = output_field

        # Calculate the other two arrays
        intensity = np.abs(output_field.field) ** 2
        phase = np.angle(output_field.field)
        # Save the arrays in an H5 file
        file_path = os.path.join(results_directory, 'output_field.h5')
        counter = 0
        while os.path.exists(f'{file_path}'):
            counter += 1
            file_path = os.path.join(results_directory, f'output_field{counter}.h5')

        with h5py.File(file_path, 'w') as f:
            f.create_dataset('intensity', data=intensity)
            f.create_dataset('phase', data=phase)
            f.create_dataset('x_vector_mm', data=beam_shaper.x_array_out / mm)

        print("Output Field data saved !")
    else:
        print("No Output Field data to save")

def save_input_beam(results_directory, beam_shaper, last_generated_beam_field):

    os.makedirs(results_directory, exist_ok=True)

    if last_generated_beam_field is not None:
        last_generated_beam_field = last_generated_beam_field

        # Calculate the other two arrays
        intensity = np.abs(last_generated_beam_field.field) ** 2
        phase = np.angle(last_generated_beam_field.field)

        # Save the arrays in an H5 file
        file_path = os.path.join(results_directory, 'input_field.h5')
        counter = 0
        while os.path.exists(f'{file_path}'):
            counter += 1
            file_path = os.path.join(results_directory, f'input_field_{counter}.h5')

        with h5py.File(file_path, 'w') as f:
            f.create_dataset('intensity', data=intensity)
            f.create_dataset('phase', data=phase)
            f.create_dataset('x_vector_mm', data=beam_shaper.x_array_out / mm)

        print("Input Field data saved !")
    else:
        print("No field data to save")
def save_mask(mask, results_directory):
    os.makedirs(results_directory, exist_ok=True)
    # Save the arrays in an H5 file
    file_path = os.path.join(results_directory, 'slm6608_at1550_WFC_unwrapped.h5')
    counter = 0
    while os.path.exists(file_path):
        counter += 1
        file_path = os.path.join(results_directory, f'mask_{counter}.h5')

    with h5py.File(file_path, 'w') as f:
        f.create_dataset('mask', data=mask)

    print("Mask data saved !")

def save_target_amplitude(target_amplitude, results_directory):
    os.makedirs(results_directory, exist_ok=True)
    # Save the arrays in an H5 file
    counter = 0
    file_path = results_directory
    while os.path.exists(file_path):
        counter += 1
        file_path = os.path.join(results_directory, f'target_amplitude_{counter}.h5')

    with h5py.File(file_path, 'w') as f:
        f.create_dataset('mask', data=target_amplitude)


def save_inverse_fourier_field(beam_shaper,inverse_fourier_field, results_directory):
        # Calculate the other two arrays
        intensity = np.abs(inverse_fourier_field.field) ** 2
        phase = np.angle(inverse_fourier_field.field)
        # Save the arrays in an H5 file
        file_path = os.path.join(results_directory, 'inverse_fourier_field.h5')
        counter = 0
        while os.path.exists(f'{file_path}'):
            counter += 1
            file_path = os.path.join(results_directory, f'inverse_fourier_field{counter}.h5')

        with h5py.File(file_path, 'w') as f:
            f.create_dataset('intensity', data=intensity)
            f.create_dataset('phase', data=phase)
            f.create_dataset('x_vector_mm', data=beam_shaper.x_array_out / mm)

        print("Output Field data saved !")


def crop_center(array_x, nb_of_samples_along_x, nb_of_samples_along_y):
    y_len, x_len = array_x.shape

    x_start = x_len//2 - nb_of_samples_along_x//2
    x_end = x_start + nb_of_samples_along_x

    # print(x_start, x_end)

    y_start = y_len//2 - nb_of_samples_along_y//2
    y_end = y_start + nb_of_samples_along_y

    if nb_of_samples_along_x<array_x.shape[1]:
        array_x_crop = array_x[:, x_start:x_end]
    if nb_of_samples_along_y<array_x.shape[0]:
        array_x_crop = array_x_crop[y_start:y_end, :]
    if nb_of_samples_along_y>=array_x.shape[0] and nb_of_samples_along_x>=array_x.shape[1]:
        array_x_crop = array_x


    return array_x_crop

from PIL import Image

def discretize_array(array, levels=256):
    # Find the min and max values in the array
    min_val = np.min(array)
    max_val = np.max(array)

    # Normalize array to [0, 1]
    normalized_array = (array - min_val) / (max_val - min_val)

    # Discretize to specified levels
    discretized_array = np.round(normalized_array * (levels - 1)).astype(int)

    # Map back to original range
    discretized_array = (discretized_array / (levels - 1)) * (max_val - min_val) + min_val


    return discretized_array
def crop_and_save_as_bmp(image, results_directory, file_name):

    crop_img = crop_center(image, 1920, 1200)
    crop_img = np.angle(np.exp(1j*crop_img))
    crop_img = (crop_img + np.pi) * 255 / (2 * np.pi)
    crop_img = discretize_array(crop_img, levels=256)


    # Convert the image to an array
    img_array = np.array(crop_img)

    # Check if the image has an alpha channel, if not, add one

    # Create a new array with shape of the image array but with an extra channel
    new_img_array = np.zeros((img_array.shape[0], img_array.shape[1], 4), dtype=np.uint8)

    # Set RGB channels
    new_img_array[:,:,0] = img_array
    # Set Alpha channel
    new_img_array[..., 3] = 255  # assuming you want a fully opaque image, otherwise adjust this value


    # Convert back to an image
    bmp_img = Image.fromarray(new_img_array)


    os.makedirs(results_directory, exist_ok=True)

    # Save the image in a BMP file
    file_path = os.path.join(results_directory, f'{file_name}.bmp')
    counter = 0
    while os.path.exists(file_path):
        counter += 1
        file_path = os.path.join(results_directory, f'{file_name}_{counter}.bmp')

    bmp_img.save(file_path)

    print("SLM Mask data saved !")

def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def downsample(array, downsample_factor):
    """
    Downsamples a 2D numpy array by averaging over blocks of size `downsample_factor`.

    Parameters
    ----------
    array : numpy.ndarray
        Input 2D array to downsample.
    downsample_factor : int
        Downsampling factor. The size of the input array should be divisible by this factor.

    Returns
    -------
    numpy.ndarray
        Downsampled array.
    """
    if not array.shape[0] % downsample_factor == 0 or not array.shape[1] % downsample_factor == 0:
        raise ValueError("Both dimensions of the input array must be divisible by the downsample factor.")

    # Reshape to a higher dimensional array
    reshaped = array.reshape((array.shape[0] // downsample_factor, downsample_factor,
                              array.shape[1] // downsample_factor, downsample_factor))

    # Take the mean over the extra dimensions
    downsampled = reshaped.mean(axis=1).mean(axis=-1)

    return downsampled

def downsample_1d(array, downsample_factor):
    """
    Downsamples a 1D numpy array by averaging over blocks of size `downsample_factor`.

    Parameters
    ----------
    array : numpy.ndarray
        Input 1D array to downsample.
    downsample_factor : int
        Downsampling factor. The size of the input array should be divisible by this factor.

    Returns
    -------
    numpy.ndarray
        Downsampled array.
    """
    if not len(array) % downsample_factor == 0:
        raise ValueError("The size of the input array must be divisible by the downsample factor.")

    # Reshape to a higher dimensional array
    reshaped = array.reshape((len(array) // downsample_factor, downsample_factor))

    # Take the mean over the extra dimension
    downsampled = reshaped.mean(axis=1)

    return downsampled

def correct_modulation_values(modulation_values,a_values,correction_tab):

    return np.interp(modulation_values,a_values,correction_tab)



