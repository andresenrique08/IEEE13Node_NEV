""" This script contains functions to handle the analysis of IEEE 13 nodes network."""

from Analysis_HC_NEV.utils.constants_ieee13nodes import NODES_ORDER, NODES_NUMBER, NODES_NUMBER_NAME, NODES_NAME
from Analysis_HC_NEV.utils.opendss_engine import DSSCircuit


def get_buses_ordered():
    """ This function returns the buses ordered by the NODES_ORDER dictionary """

    bus_names = list(DSSCircuit.AllBusNames)
    for bus in bus_names:
        if bus not in NODES_ORDER:
            print(f"Warning: Bus {bus} not found in the dictionary")
            bus_names.remove(bus)
    return sorted(bus_names, key=lambda x: NODES_ORDER[x])


def filter_loads(
        load_names_fixed: list,
        bus: str = None,
        n_phases: int = None,
        conn: str = None,
        model: int = None,
        kv: float = None
):
    """ This function filters the loads in the network
    @:params
    load_names_fixed: list, the names of the loads in the network. This list is not modified
    bus: str, the name of the bus to filter the loads
    n_phases: int, the number of phases of the loads
    conn: str, the connection type of the loads
    model: int, the model of the loads
    kv: float, the voltage of the loads
    @:return
    load_names: list, the names of the loads filtered in the network"""

    load_names = list(DSSCircuit.Loads.AllNames)
    values = [bus, n_phases, conn, model, kv]
    for load in load_names_fixed:
        DSSCircuit.SetActiveElement(f'load.{load}')
        bus_name = DSSCircuit.ActiveElement.Properties('bus1').Val
        phases = int(DSSCircuit.ActiveElement.Properties('phases').Val)
        connection = DSSCircuit.ActiveElement.Properties('conn').Val
        model_sis = DSSCircuit.ActiveElement.Properties('model').Val
        kv_value = DSSCircuit.ActiveElement.Properties('kv').Val
        values_sis = [bus_name, phases, connection, model_sis, kv_value]
        for i in range(len(values)):
            if values[i] is None:
                values_sis[i] = None

        if values != values_sis:
            load_names.remove(load)

    return load_names


def get_mag_voltages(bus_names: list, mag_pu: bool = False, show_message: bool = True):
    # Create the dictionary to store the voltages
    voltages = {}

    for bus_name in bus_names:
        # Get the active bus
        active_bus = DSSCircuit.ActiveBus(bus_name)
        # Get the voltages
        v_mag_angle = active_bus.puVmagAngle if mag_pu else active_bus.VMagAngle
        # Get the nodes of the bus
        nodes = active_bus.Nodes
        # Create the key in the dictionary for the bus
        voltages[bus_name] = {}
        for i, node in enumerate(nodes):
            if node in NODES_NUMBER:
                # Get the name of the node
                node_name = NODES_NUMBER_NAME[node]
                # Store the voltage in the dictionary
                voltages[bus_name][node_name] = v_mag_angle[i * 2]
            elif show_message:
                print(f"Warning: Node {node} not found in the dictionary for the bus {bus_name}")

    return voltages


def get_vuf_3ph(bus_names: list, n_phases: int = 3):
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
    # Create the dictionary to store the currents
    currents = {}

    for line in line_names:
        DSSCircuit.SetActiveElement(f'line.{line}')
        bus_name = DSSCircuit.ActiveElement.Properties('bus1').Val.split('.')[0]
        # Get the currents
        currents_mag_ang = DSSCircuit.ActiveElement.CurrentsMagAng
        # Get the active bus
        active_bus = DSSCircuit.ActiveBus(bus_name)
        # Get the nodes of the bus
        nodes = active_bus.Nodes
        # Create the key in the dictionary for the line
        currents[line] = {}
        for i, node in enumerate(nodes):
            if node in NODES_NUMBER:
                # Get the name of the node
                node_name = NODES_NUMBER_NAME[node]
                # Store the current in the dictionary
                currents[line][node_name] = currents_mag_ang[i * 2]
            elif show_message:
                print(f"Warning: Node {node} not found in the dictionary for the line {line}")

    return currents
