""" This script contains functions to handle the analysis of any network. """
import pandas as pd


def get_error_between_two_values(value1, value2):
    """
    This function calculates the error between two values.
    @param value1: value 1
    @param value2: value 2
    @return: error in percentage
    """
    error = abs(value1 - value2) * 100
    return error


def get_error_between_two_dict(dict1, dict2):
    """
    This function calculates the error between two dictionaries of dictionaries.
    @param dict1: dictionary of dictionaries
    @param dict2: dictionary of dictionaries
    @return: dictionary of dictionaries with the error in percentage
    """
    error = {}
    for key, sec_keys in dict1.items():
        for sec_key, value in sec_keys.items():
            if key not in error:
                error[key] = {}
            if sec_key not in error[key]:
                error[key][sec_key] = get_error_between_two_values(value, dict2[key][sec_key])
    return error


def find_max_in_dictionary(dictionary: dict):
    """
    This function finds the maximum value in a dictionary of dictionaries.
    @param dictionary: dictionary of dictionaries
    @return: maximum value in the dictionary
    """
    maximum = max([max(value.values()) for value in dictionary.values()])
    return maximum


def find_min_in_dictionary(dictionary: dict):
    """
    This function finds the minimum value in a dictionary of dictionaries.
    @param dictionary: dictionary of dictionaries
    @return: minimum value in the dictionary
    """
    minimum = min([min(value.values()) for value in dictionary.values()])
    return minimum


def get_dataframe_from_dict(
        dictionary: dict,
        column_names=None,
        dictionary_sec: bool = False):
    """
    This function creates a DataFrame from a dictionary of dictionaries.
    @param dictionary: dictionary of dictionaries
    @param column_names: column names
    @param dictionary_sec: if the dictionary is a dictionary of dictionaries
    @return: DataFrame
    """
    if column_names is None:
        column_names = ['Bus', 'Data']

    df = pd.DataFrame(dictionary.items(), columns=column_names)

    if dictionary_sec:
        df = pd.concat([df[column_names[0]], df[column_names[1]].apply(pd.Series)], axis=1)

    return df
