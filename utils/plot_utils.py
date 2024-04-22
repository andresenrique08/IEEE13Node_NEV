import numpy as np
from matplotlib import pyplot as plt
from Analysis_HC_NEV.utils.utils import *
from Analysis_HC_NEV.utils.constants_ieee13nodes import *


def save_plot(fig: plt.Figure, name: str, background_color: str = 'white'):
    """
    This function saves the plot as an image with a background.
    @param fig: figure
    @param name: name of the image
    @param background_color: background color
    """
    # Set the background color
    fig.patch.set_facecolor(background_color)

    # Save the graph as an image with a white background
    fig.savefig(name, bbox_inches='tight')


def latex_parameters_plot(font_size: int, font_family: str):
    plt.rcParams.update({
        "text.usetex": True,  # Use LaTeX
        "font.family": font_family,  # Font family
        "font.serif": ["Computer Modern"],  # Font
        "font.size": font_size,  # Font size
    })


def normal_parameters_plot(font_size: int, font_family: str):
    plt.rcParams.update({
        "text.usetex": False,
        "font.family": font_family,
        "font.size": font_size,
    })


def latex_bold(text: str):
    return r"\textbf{" + text + "}"


def latex_normal(text: str):
    return r'' + text


def latex_cursive(text: str):
    return r"\textif{" + text + "}"


def get_text_formatted(text: str, is_bold: bool = False):
    return None if text is None else latex_bold(text) if is_bold else latex_normal(text)


def get_color_by_phase():
    return {'a': '#6C8EBF', 'b': '#82B366', 'c': '#B85450', 'n': 'black'}


def get_color_list_random():
    return ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

def plot_bar_dict(
        data: dict,
        latex_style: bool = False,
        font_size: int = 14,
        font_family: str = 'Times New Roman',
        title: str = None,
        title_bold: bool = True,
        title_x: str = None,
        title_y: str = None,
        color: str = 'b',
        size: tuple = (10, 6),
        bar_width: float = 0.25,
        show_value: bool = True,
        is_percentage: bool = False,
        span_text: float = 0.02,
        rotation_text: int = 90,
        fontsize_text: int = 8,
        horizontal_limit: float = None,
        color_horizontal_limit: str = 'r'
):
    """
    This function plots bars from one dictionary with keys and values.
    @param data: dictionary of dictionaries with the error in percentage
    @param latex_style: boolean to set the latex style
    @param font_size: font size for latex
    @param font_family: font family for latex
    @param title: title of the plot
    @param title_bold: boolean to set the title in bold
    @param title_x: title of the x-axis
    @param title_y: title of the y-axis
    @param color: string with the color of the bars
    @param size: size of the plot
    @param bar_width: width of the bars
    @param show_value: boolean to set if the value is showed
    @param is_percentage: boolean to set if the text is with percentage
    @param span_text: span of the text
    @param rotation_text: rotation of the text
    @param fontsize_text: fontsize of the text
    @param horizontal_limit: Value for a horizontal line
    @param color_horizontal_limit: Color for the horizontal line
    @return: plt
    """

    # if latex_style is True, set the style to latex
    # Note: To use LaTeX, you need to have LaTeX installed in your computer
    if latex_style:
        latex_parameters_plot(font_size, font_family)
        title = get_text_formatted(title, title_bold)
        title_x = get_text_formatted(title_x)
        title_y = get_text_formatted(title_y)
    else:
        normal_parameters_plot(font_size, font_family)

    fig, ax = plt.subplots(figsize=size)
    if horizontal_limit is not None:
        plt.axhline(y=horizontal_limit, color=color_horizontal_limit, linestyle='--')

    # Iter in the dictionary
    for i, (key, value) in enumerate(data.items()):
        # Add bars to the plot
        ax.bar(i, value, width=bar_width, color=color)
        if show_value:
            # Add text to the plot
            format_value = f'{value:.2f}%' if is_percentage else f'{value:.2f}'
            ax.text(i, value + span_text, format_value, ha='center', rotation=rotation_text,
                    fontsize=fontsize_text)

    maximum = max(data.values()) if horizontal_limit is None else max(max(data.values()), horizontal_limit)
    # Configuring the plot
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.keys())
    ax.set_ylim(0, maximum + span_text * 4)
    ax.set_xlabel(title_x)
    ax.set_ylabel(title_y)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    return fig


def plot_bar_dict_dict(
        data: dict,
        latex_style: bool = False,
        font_size: int = 14,
        font_family: str = 'Times New Roman',
        title: str = None,
        title_bold: bool = True,
        title_x: str = None,
        title_y: str = None,
        show_legend: bool = True,
        title_legend: str = None,
        loc_legend: str = 'upper left',
        colors: dict = None,
        size: tuple = (10, 6),
        bar_width: float = 0.25,
        show_value: bool = True,
        is_percentage: bool = False,
        span_text: float = 0.02,
        rotation_text: int = 90,
        fontsize_text: int = 8
):
    """
    This function plots bars from a dictionary containing dictionaries.
    @param data: dictionary of dictionaries with the error in percentage
    @param latex_style: boolean to set the latex style
    @param font_size: font size for latex
    @param font_family: font family for latex
    @param title: title of the plot
    @param title_bold: boolean to set the title in bold
    @param title_x: title of the x-axis
    @param title_y: title of the y-axis
    @param show_legend: boolean to show the legend
    @param title_legend: title of the legend
    @param loc_legend: location of the legend
    @param colors: dictionary with the colors for each phase
    @param size: size of the plot
    @param bar_width: width of the bars
    @param show_value: boolean to set if the value is showed
    @param is_percentage: boolean to set if the text is with percentage
    @param span_text: span of the text
    @param rotation_text: rotation of the text
    @param fontsize_text: fontsize of the text
    @return: plt
    """

    # if latex_style is True, set the style to latex
    # Note: To use LaTeX, you need to have LaTeX installed in your computer
    if latex_style:
        latex_parameters_plot(font_size, font_family)
        title = get_text_formatted(title, title_bold)
        title_x = get_text_formatted(title_x)
        title_y = get_text_formatted(title_y)
        title_legend = get_text_formatted(title_legend)
    else:
        normal_parameters_plot(font_size, font_family)

    # If colors is None, set default colors
    if colors is None:
        colors = get_color_by_phase()

    fig, ax = plt.subplots(figsize=size)

    maximum = 0
    # Iter in the error dictionary
    for i, (key, dict_values) in enumerate(data.items()):
        # Names of the keys in the dictionary
        sec_keys = list(dict_values.keys())
        # Validate if every value in the dictionary of values is numeric
        all_numeric = all(isinstance(value, (int, float)) for value in dict_values.values())
        if all_numeric:
            if i == 0:
                maximum = find_max_in_dictionary(data)
            # Positions for each bar
            positions = [i + bar_width * j for j in range(len(dict_values))]
            # Values of the errors
            values = [value for value in dict_values.values()]

            # Add bars to the plot
            for j, sec_key in enumerate(sec_keys):
                ax.bar(positions[j], values[j], width=bar_width, color=colors[sec_key],
                       label=sec_key if i == 0 else None)
                if show_value:
                    # Add text to the plot
                    format_value = f'{values[j]:.2f}%' if is_percentage else f'{values[j]:.2f}'
                    ax.text(positions[j], values[j] + span_text, format_value, ha='center', rotation=rotation_text,
                            fontsize=fontsize_text)
        else:
            if i == 0:
                maximum = max(entry[sec_keys[0]] for entry in data.values())
            try:
                ax.bar(i, dict_values[sec_keys[0]], width=bar_width, color=colors[sec_keys[0]],
                       label=sec_keys[0] if i == 0 else None)
            except KeyError:
                ax.bar(i, dict_values[sec_keys[0]], width=bar_width, color='black',
                       label=sec_keys[0] if i == 0 else None)
            if show_value:
                # Add text to the plot
                format_value = f'{dict_values[sec_keys[1]]}'
                ax.text(i, dict_values[sec_keys[0]] + span_text, format_value, ha='center', rotation=rotation_text,
                        fontsize=fontsize_text)

    # Configuring the plot
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.keys())
    ax.set_ylim(0, maximum + span_text * 6)
    ax.set_xlabel(title_x)
    ax.set_ylabel(title_y)
    if show_legend:
        ax.legend(title=title_legend, loc=loc_legend)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    return fig


def plot_bar_dict_dict_dict(
        data: dict,
        latex_style: bool = False,
        font_size: int = 14,
        font_family: str = 'Times New Roman',
        title: str = None,
        title_bold: bool = True,
        title_x: str = None,
        title_y: str = None,
        show_legend: bool = True,
        title_legend: str = None,
        loc_legend: str = 'upper left',
        colors: list = None,
        size: tuple = (10, 6),
        bar_width: float = 0.25,
        show_value: bool = True,
        span_text: float = 0.02,
        rotation_text: int = 90,
        fontsize_text: int = 8,
        span_min_max: float = 0
):
    """
    This function plots bars from a dictionary containing dictionaries.
    :param data: dictionary of dictionaries with the error in percentage
    :param latex_style: boolean to set the latex style
    :param font_size: font size for latex
    :param font_family: font family for latex
    :param title: title of the plot
    :param title_bold: boolean to set the title in bold
    :param title_x: title of the x-axis
    :param title_y: title of the y-axis
    :param show_legend: boolean to show the legend
    :param title_legend: title of the legend
    :param loc_legend: location of the legend
    :param colors: dictionary with the colors for each phase
    :param size: size of the plot
    :param bar_width: width of the bars
    :param show_value: boolean to set if the value is showed
    :param span_text: span of the text
    :param rotation_text: rotation of the text
    :param fontsize_text: fontsize of the text
    :param span_min_max: span of the min and max values
    :return:
    """

    # if latex_style is True, set the style to latex
    # Note: To use LaTeX, you need to have LaTeX installed in your computer

    if latex_style:
        latex_parameters_plot(font_size, font_family)
        title = get_text_formatted(title, title_bold)
        title_x = get_text_formatted(title_x)
        title_y = get_text_formatted(title_y)
        title_legend = get_text_formatted(title_legend)
    else:
        normal_parameters_plot(font_size, font_family)

    # If colors is None, set default colors
    if colors is None:
        colors = get_color_list_random()


    fig, ax = plt.subplots(figsize=size)

    maximum = 0
    minimum = 0
    # Iter in the error dictionary
    for i, (key, dict_values) in enumerate(data.items()):
        if i == 0:
            x_names = list(dict_values.keys())
        for j, (sec_key, sec_dict_values) in enumerate(dict_values.items()):
            # Names of the keys in the dictionary
            ter_keys = list(sec_dict_values.keys())
            if j == 0:
                maximum = max(max(entry[ter_keys[0]] for entry in dict_values.values()), maximum)
                maximum = maximum if maximum > 0 else 0
                minimum = min(min(entry[ter_keys[0]] for entry in dict_values.values()), minimum)
                minimum = minimum if minimum < 0 else 0
            # Positions for each bar
            positions = [j + bar_width * k for k in range(len(data.keys()))]
            # Values of the inner dictionary
            value = list(sec_dict_values.values())[0]
            # Add bars to the plot
            ax.bar(positions[i], value, width=bar_width, color=colors[i], label=key if j == 0 else None)
            if show_value:
                format_value = f'{sec_dict_values[ter_keys[1]]}'
                initial_position = span_text if value == 0 else value + span_text
                ax.text(positions[i], initial_position, format_value, ha='center', rotation=rotation_text,
                        fontsize=fontsize_text)

    # Configuring the plot
    ax.set_xticks(range(len(x_names)))
    ax.set_xticklabels(x_names)
    ax.set_ylim(
        minimum - span_min_max if minimum < 0 else minimum,
        maximum + span_min_max if maximum > 0 else maximum
    )
    ax.set_xlabel(title_x)
    ax.set_ylabel(title_y)
    if show_legend:
        ax.legend(title=title_legend, loc=loc_legend)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    return fig


def plot_voltage_line_dict_dict(
        data: dict,
        delete_zeros: bool = False,
        keys_to_delete: list = None,
        latex_style: bool = False,
        font_size: int = 14,
        font_family: str = 'Times New Roman',
        title: str = None,
        title_bold: bool = True,
        title_x: str = None,
        title_y: str = None,
        show_legend: bool = True,
        title_legend: str = None,
        loc_legend: str = 'upper left',
        colors: dict = None,
        size: tuple = (10, 6),
        limit_top: float = None,
        color_limit_top: str = 'r',
        limit_bottom: float = None,
        color_limit_bottom: str = 'r',
        span_plot: float = 0.1,
        line_width: float = 1
):
    """
    This function plots lines from a dictionary containing dictionaries.
    :param data: dictionary of dictionaries with the error in percentage
    :param delete_zeros: boolean to delete the zeros
    :param keys_to_delete: list of keys to delete
    :param latex_style: boolean to set the latex style
    :param font_size: font size for latex
    :param font_family: font family for latex
    :param title: title of the plot
    :param title_bold: boolean to set the title in bold
    :param title_x: title of the x-axis
    :param title_y: title of the y-axis
    :param show_legend: boolean to show the legend
    :param title_legend: title of the legend
    :param loc_legend: location of the legend
    :param colors: dictionary with the colors for each phase
    :param size: size of the plot
    :param limit_top: Value for a horizontal line
    :param color_limit_top: Color for the horizontal line
    :param limit_bottom: Value for a horizontal line
    :param color_limit_bottom: Color for the horizontal line
    :param span_plot: span of the plot
    :param line_width: width of the line
    :return: plt
    """
    # Data transformation
    if delete_zeros:
        data = {bus: {node: value for node, value in data[bus].items() if value != 0} for bus in data.keys()}
    x_names = list(data.keys())
    y_values = {node: [np.nan if node not in data[bus] else data[bus][node] for bus in x_names] for node in NODES_NAME}

    if keys_to_delete is not None:
        for key in keys_to_delete:
            del y_values[key]

    # if latex_style is True, set the style to latex
    # Note: To use LaTeX, you need to have LaTeX installed in your computer
    if latex_style:
        latex_parameters_plot(font_size, font_family)
        title = get_text_formatted(title, title_bold)
        title_x = get_text_formatted(title_x)
        title_y = get_text_formatted(title_y)
    else:
        normal_parameters_plot(font_size, font_family)

    fig, ax = plt.subplots(figsize=size)

    if limit_top is not None:
        plt.axhline(y=limit_top, color=color_limit_top, linestyle='--')
    if limit_bottom is not None:
        plt.axhline(y=limit_bottom, color=color_limit_bottom, linestyle='--')

    # If colors is None, set default colors
    if colors is None:
        colors = get_color_by_phase()

    for node in NODES_NAME:
        if node in y_values.keys():
            # Plotting the voltages
            plt.plot(x_names, y_values[node], label=f"Phase {node}", marker='*', color=colors[node],
                     linewidth=line_width)

    all_y_values = [value for values in list(y_values.values()) for value in values]
    maximum = np.nanmax(all_y_values) if limit_top is None else max(np.nanmax(all_y_values), limit_top)
    minimum = np.nanmin(all_y_values) if limit_bottom is None else min(
        np.nanmin(all_y_values), limit_bottom)
    # Configuring the plot
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.keys())
    ax.set_ylim(minimum - span_plot, maximum + span_plot)
    ax.set_xlabel(title_x)
    ax.set_ylabel(title_y)
    if show_legend:
        ax.legend(title=title_legend, loc=loc_legend)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    return fig


def plot_line_dict_dict(
        data: dict,
        delete_zeros: bool = False,
        keys_to_delete: list = None,
        latex_style: bool = False,
        font_size: int = 14,
        font_family: str = 'Times New Roman',
        title: str = None,
        title_bold: bool = True,
        title_x: str = None,
        title_y: str = None,
        show_legend: bool = True,
        title_legend: str = None,
        legend_names: list = None,
        loc_legend: str = 'upper left',
        colors: list = None,
        size: tuple = (10, 6),
        limit_top: float = None,
        color_limit_top: str = 'r',
        limit_bottom: float = None,
        color_limit_bottom: str = 'r',
        span_plot: float = 0.1,
        marker: str = '*',
        linestyle: list = None,
        line_width: float = 1
):
    """
    This function plots lines from a dictionary containing dictionaries.
    :param data: dictionary of dictionaries with the error in percentage
    :param delete_zeros: boolean to delete the zeros
    :param keys_to_delete: list of keys to delete
    :param latex_style: boolean to set the latex style
    :param font_size: font size for latex
    :param font_family: font family for latex
    :param title: title of the plot
    :param title_bold: boolean to set the title in bold
    :param title_x: title of the x-axis
    :param title_y: title of the y-axis
    :param show_legend: boolean to show the legend
    :param title_legend: title of the legend
    :param legend_names: names of the legend
    :param loc_legend: location of the legend
    :param colors: dictionary with the colors for each phase
    :param size: size of the plot
    :param limit_top: Value for a horizontal line
    :param color_limit_top: Color for the horizontal line
    :param limit_bottom: Value for a horizontal line
    :param color_limit_bottom: Color for the horizontal line
    :param span_plot: span of the plot
    :param marker: marker for the plot
    :param linestyle: linestyle for the plot
    :param line_width: width of the line
    :return: plt
    """
    # Data transformation
    if delete_zeros:
        data = {bus: {node: value for node, value in data[bus].items() if value != 0} for bus in data.keys()}
    x_names = list(data.keys())
    internal_keys = list(list(data.values())[0].keys())
    y_values = {iKey: [np.nan if iKey not in data[bus] else data[bus][iKey] for bus in x_names] for iKey in internal_keys}

    if keys_to_delete is not None:
        for key in keys_to_delete:
            del y_values[key]

    # if latex_style is True, set the style to latex
    # Note: To use LaTeX, you need to have LaTeX installed in your computer
    if latex_style:
        latex_parameters_plot(font_size, font_family)
        title = get_text_formatted(title, title_bold)
        title_x = get_text_formatted(title_x)
        title_y = get_text_formatted(title_y)
    else:
        normal_parameters_plot(font_size, font_family)

    fig, ax = plt.subplots(figsize=size)

    if limit_top is not None:
        plt.axhline(y=limit_top, color=color_limit_top, linestyle='--')
    if limit_bottom is not None:
        plt.axhline(y=limit_bottom, color=color_limit_bottom, linestyle='--')

    # If colors is None, set default colors
    if colors is None:
        colors = get_color_list_random()

    if legend_names is None:
        legend_names = [i for i in y_values.keys()]

    if linestyle is None:
        linestyle = ['-' for _ in range(len(internal_keys))]

    for i in range(len(internal_keys)):
        key = internal_keys[i]
        if key in y_values.keys():
            # Plotting the voltages
            plt.plot(x_names, y_values[key], label=legend_names[i], marker=marker, color=colors[i],
                     linestyle=linestyle[i], linewidth=line_width)

    all_y_values = [value for values in list(y_values.values()) for value in values]
    maximum = np.nanmax(all_y_values) if limit_top is None else max(np.nanmax(all_y_values), limit_top)
    minimum = np.nanmin(all_y_values) if limit_bottom is None else min(
        np.nanmin(all_y_values), limit_bottom)
    # Configuring the plot
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(data.keys())
    ax.set_ylim(minimum - span_plot, maximum + span_plot)
    ax.set_xlabel(title_x)
    ax.set_ylabel(title_y)
    if show_legend:
        ax.legend(title=title_legend, loc=loc_legend)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()

    return fig
