""" This script is intended to be used to handle the files in the project. """

import os


def get_file_path(file_name: str):
    # Get the current directory
    my_directory = os.getcwd()

    # Defining the file path
    file_path = os.path.abspath(os.path.join(my_directory, file_name))
    print("The file path is: ", file_path)

    return file_path


def get_root_directory():
    # Get the current directory
    my_directory = os.getcwd()

    # Get the root directory
    root_directory = os.path.abspath(os.path.join(my_directory, os.pardir))

    return root_directory
