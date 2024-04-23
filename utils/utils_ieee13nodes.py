""" This script contains functions to handle the analysis of IEEE 13 nodes network."""

from Utils.constants_ieee13nodes import NODES_ORDER, NODES_NUMBER, NODES_NUMBER_NAME
from Utils.opendss_engine import DSSCircuit


def get_buses_ordered():
    """
    This function returns the buses ordered by the NODES_ORDER dictionary
    @:params -> None
    @:return -> bus_names: list, the names of the buses ordered by the NODES_ORDER dictionary
    """

    bus_names = list(DSSCircuit.AllBusNames)
    for bus in bus_names:
        if bus not in NODES_ORDER:
            print(f"Warning: Bus {bus} not found in the dictionary")
            bus_names.remove(bus)
    return sorted(bus_names, key=lambda x: NODES_ORDER[x])


def get_mag_voltages(bus_names: list, mag_pu: bool = False, show_message: bool = True):
    """
    This function gets the magnitude of the voltages in the IEEE 13 nodes network.
    @:params
    bus_names: list, the names of the buses
    mag_pu: bool, if we want the values in per unit
    show_message: bool, if we want to show the messages
    @:return
    voltages: dict, the magnitude of the voltages in the IEEE 13 nodes network.
    """
    # Create the dictionary to store the voltages
    voltages = {}

    for bus_name in bus_names:
        # Get the active bus
        active_bus = DSSCircuit.ActiveBus(bus_name)
        # Get the voltages
        v_mag_angle = active_bus.puVmagAngle if mag_pu else active_bus.VMagAngle
        # Get the values for the voltage
        voltages = get_dict_magnitude_by_element(
            active_bus_name=bus_name,
            element=bus_name,
            values=voltages,
            show_message=show_message,
            values_magnitude=v_mag_angle
        )

    return voltages


def get_vuf_3ph(bus_names: list, n_phases: int = 3):
    """
    This function gets the Voltage Unbalance Factor (VUF) of the IEEE 13 nodes network.
    @:params
    bus_names: list, the names of the buses
    n_phases: int, the number of phases
    @:return
    vuf: dict, the Voltage Unbalance Factor (VUF) of the IEEE 13 nodes network.
    """
    # Create the dictionary to store the Voltage Unbalance Factor (VUF)
    vuf = {}

    for bus_name in bus_names:
        # Get the active bus
        active_bus = DSSCircuit.ActiveBus(bus_name)

        if len(active_bus.Nodes) > n_phases:
            # Get the voltages
            seq_voltages = active_bus.SeqVoltages
            # Calculate the VUF
            if seq_voltages[1] > 0:
                vuf[bus_name] = (seq_voltages[2] / seq_voltages[1]) * 100

    return vuf


def get_mag_currents(line_names: list, show_message: bool = True):
    """
    This function gets the magnitude of the currents in the IEEE 13 nodes network.
    @:params
    line_names: list, the names of the lines
    show_message: bool, if we want to show the messages
    @:return
    currents: dict, the magnitude of the currents in the IEEE 13 nodes network.
    """
    # Create the dictionary to store the currents
    currents = {}

    for line in line_names:
        DSSCircuit.SetActiveElement(f'line.{line}')
        bus_name = DSSCircuit.ActiveElement.Properties('bus1').Val.split('.')[0]
        # Get the currents
        currents_mag_ang = DSSCircuit.ActiveElement.CurrentsMagAng
        # Get the values for the current
        currents = get_dict_magnitude_by_element(
            active_bus_name=bus_name,
            element=line,
            values=currents,
            show_message=show_message,
            values_magnitude=currents_mag_ang
        )

    return currents


def get_dict_magnitude_by_element(
        active_bus_name: str,
        element: str,
        values: dict,
        show_message: bool,
        values_magnitude):
    """
    This function helps to get the values for the dictionaries of voltages and currents
    @:params
    active_bus_name: str, the name of the active bus
    element: str, the element that we are analyzing
    values: dict, the dictionary to store the values
    show_message: bool, if we want to show the messages
    values_magnitude: list, the values of the magnitude
    @:return
    values: dict, the dictionary with the values
    """
    # Get the active bus
    active_bus = DSSCircuit.ActiveBus(active_bus_name)
    # Get the nodes of the bus
    nodes = active_bus.Nodes
    # Create the dictionary to store the values
    values[element] = {}
    for i, node in enumerate(nodes):
        if node in NODES_NUMBER:
            # Get the name of the node
            node_name = NODES_NUMBER_NAME[node]
            # Store the value in the dictionary
            values[element][node_name] = values_magnitude[i * 2]
        elif show_message:
            print(f"Warning: Node {node} not found in the dictionary for the {element}")

    return values
