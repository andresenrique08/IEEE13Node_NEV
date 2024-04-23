""" This class contains functions to handle the analysis of IEEE 13 nodes network."""

# Import the necessary libraries and dependencies
import numpy as np
from Utils.opendss_engine import *
from Utils.utils_ieee13nodes import *

PERIOD = "."
NONE = "NONE"


class IEEE13Nodes:
    def __init__(
            self,
            circuit_path: str,
            open_switch: bool = False,
            neutral_node: int = 4,
            ground_node: int = 0,
            earth_model: str = None,
            has_neutral: bool = False
    ):
        self.circuit_path = circuit_path
        self.open_switch = open_switch
        self.neutral_node = neutral_node
        self.ground_node = ground_node
        self.DSSCircuit = DSSCircuit
        self.has_neutral = has_neutral

        # Compile the circuit
        DSSText.Command = "Compile " + self.circuit_path

        if earth_model is not None:
            DSSText.Command = f"Set earthmodel = {earth_model}"

        # Manage the switch
        self.manage_switch()

        # Initialize the elements of the circuit
        self.lines_names = list(DSSCircuit.Lines.AllNames)
        self.transformers_names = list(DSSCircuit.Transformers.AllNames)
        self.buses_names = None
        self.load_names = list(DSSCircuit.Loads.AllNames)
        self.pv_systems = list(DSSCircuit.PVSystems.AllNames)
        self.reactor_names = list(DSSCircuit.Reactors.AllNames)
        self.reg_controls = list(DSSCircuit.RegControls.AllNames)

        DSSText.Command = "calcv"

    def run_power_flow(self):
        """ This function solves the power flow of the IEEE 13 nodes network.
        @:params -> None
        @:return -> None """

        DSSSolution.Solve()
        if DSSSolution.Converged:
            print("The circuit has converged successfully!")

            # Get the buses of the circuit
            self.buses_names = get_buses_ordered()
        else:
            print("The circuit has not converged")

    def restart_reg_controls(self):
        """ This function restarts the RegControls of the IEEE 13 nodes network.
        @:params -> None
        @:return -> None """

        for reg_control in self.reg_controls:
            DSSCircuit.SetActiveElement(f'regcontrol.{reg_control}')
            DSSCircuit.ActiveElement.Properties('tapnum').Val = 0

    def do_kron_reduction(self):
        """ This function performs the Kron reduction of the IEEE 13 nodes network when the neutral wire is modeled.
        @:params -> None
        @:return -> None """

        neutral_node = self.neutral_node
        ground_node = self.ground_node
        self.has_neutral = False

        # Creating a reduction in the lines
        for line in self.lines_names:
            DSSCircuit.SetActiveElement(f'line.{line}')
            bus1 = DSSCircuit.ActiveElement.Properties('bus1').Val
            bus2 = DSSCircuit.ActiveElement.Properties('bus2').Val
            if len(bus1.split(PERIOD)) > 1:
                if int(bus1.rsplit(PERIOD, maxsplit=1)[1]) == neutral_node:
                    DSSCircuit.ActiveElement.Properties('bus1').Val = \
                        bus1.rsplit(PERIOD, maxsplit=1)[0] + f'.{ground_node}'
                    DSSCircuit.ActiveElement.Properties('bus2').Val = \
                        bus2.rsplit(PERIOD, maxsplit=1)[0] + f'.{ground_node}'

        # Delete the neutral connection in loads
        for load in self.load_names:
            DSSCircuit.SetActiveElement('load.' + load)
            bus1 = DSSCircuit.ActiveElement.Properties('bus1').Val
            if int(bus1.rsplit(PERIOD, maxsplit=1)[1]) == neutral_node:
                DSSCircuit.ActiveElement.Properties('bus1').Val = bus1.rsplit(PERIOD, maxsplit=1)[0]

        # Delete the neutral connection in trafos
        for trafo in self.transformers_names:
            DSSCircuit.SetActiveElement('transformer.' + trafo)
            bus1 = DSSCircuit.ActiveElement.BusNames[0]
            bus2 = DSSCircuit.ActiveElement.BusNames[1]
            if len(bus1.rsplit(PERIOD, maxsplit=1)) > 1:
                if int(bus1.rsplit(PERIOD, maxsplit=1)[1]) == neutral_node:
                    DSSCircuit.ActiveElement.BusNames[0] = bus1.rsplit(PERIOD, maxsplit=1)[0]
            if len(bus2.rsplit(PERIOD, maxsplit=1)) > 1:
                if int(bus2.rsplit(PERIOD, maxsplit=1)[1]) == neutral_node:
                    DSSCircuit.ActiveElement.BusNames[1] = bus2.rsplit(PERIOD, maxsplit=1)[0]

    def manage_switch(self):
        """ This function manages the switch in the line 671692
        :@params -> None
        :@return -> None"""

        open_switch = self.open_switch

        DSSCircuit.SetActiveElement('line.671692')
        bus1 = DSSCircuit.ActiveElement.Properties('bus1').Val
        bus2 = DSSCircuit.ActiveElement.Properties('bus2').Val

        if len(bus1.split(PERIOD)) > 1:
            if not open_switch:
                DSSCircuit.ActiveElement.Properties('bus1').Val = bus1.split(PERIOD)[0]
                DSSCircuit.ActiveElement.Properties('bus2').Val = bus2.split(PERIOD)[0]
        else:
            if open_switch:
                DSSCircuit.ActiveElement.Properties('bus1').Val = bus1 + f'.11.12.13'
                DSSCircuit.ActiveElement.Properties('bus2').Val = bus2 + f'.1.2.3'

    def add_reactors(self, z_g: complex):
        """ This function adds reactors to the IEEE 13 nodes network.
        The reactors are added in the bus 2 of each line, and it is connected in the neutral bus to the ground.
        @:params
        z_g: complex, the impedance of the reactor.
        @:return -> None """

        neutral_node = self.neutral_node
        ground_node = self.ground_node

        # Add neutral connections to the trafos
        # This only works for 2 windings
        for trafo in self.transformers_names:
            DSSCircuit.SetActiveElement('transformer.' + trafo)
            bus1 = DSSCircuit.ActiveElement.BusNames[0]
            bus2 = DSSCircuit.ActiveElement.BusNames[1]
            buses = [bus1, bus2]
            for bus in buses:
                if len(bus.rsplit(PERIOD, maxsplit=1)) > 1:
                    if int(bus.rsplit(PERIOD, maxsplit=1)[1]) != neutral_node:
                        DSSCircuit.ActiveElement.BusNames[buses.index(bus)] = bus + f'.{neutral_node}'
                else:
                    DSSCircuit.ActiveElement.BusNames[buses.index(bus)] = bus + f'1.2.3.{neutral_node}'

        # Add reactor to trafos
        DSSText.Command = (f"New Reactor.bus650 phases=1 bus1=650.{neutral_node} bus2=650.{ground_node} "
                           f"R = {np.real(z_g)} X = {np.imag(z_g)}")
        DSSText.Command = (f"New Reactor.JumperReg1 phases=1 bus1=650.{neutral_node} Bus2=RG60.{neutral_node} "
                           f"R=0.00001 X=0")
        DSSText.Command = (f"New Reactor.JumperXFM1 phases=1 bus1=633.{neutral_node} bus2=634.{neutral_node} "
                           f"R = 0.00001 X = 0")

        # Add reactor to lines
        for line in self.lines_names:
            DSSCircuit.SetActiveElement(f'line.{line}')
            bus_name = DSSCircuit.ActiveElement.Properties('bus2').Val.split('.')[0]
            active_bus = DSSCircuit.ActiveBus(bus_name)
            nodes = active_bus.Nodes
            if neutral_node in nodes and f'bus{bus_name}' not in self.reactor_names:
                DSSText.Command = (f"New Reactor.bus{bus_name} Ground Phases = 1 Bus1 = {bus_name}.{neutral_node} "
                                   f"Bus2 = {bus_name}.{ground_node} R = {np.real(z_g)} X = {np.imag(z_g)}")
            elif neutral_node in nodes:
                print(f"Reactor in bus {bus_name} already in the network.")

        self.reactor_names = list(DSSCircuit.Reactors.AllNames)
        if len(self.reactor_names) == 0:
            print("There were added no reactors to the network. Please check the buses of the lines and verify if the "
                  "is neutral wire.")


    def get_mag_voltages_pu(self):
        """ This function gets the magnitude of the voltages in per unit of the IEEE 13 nodes network.
        @:params -> None
        @:return
        voltages_pu: dict, the magnitude of the voltages in per unit of the IEEE 13 nodes network. """

        bus_names = self.buses_names
        voltages_pu = get_mag_voltages(bus_names=bus_names, mag_pu=True)

        return voltages_pu

    def get_mag_voltages(self):
        """ This function gets the magnitude of the voltages in Volts of the IEEE 13 nodes network.
        @:params -> None
        @:return
        voltages: dict, the magnitude of the voltages in Volts of the IEEE 13 nodes network. """

        bus_names = self.buses_names
        voltages = get_mag_voltages(bus_names=bus_names, mag_pu=False)

        return voltages

    def get_vuf_3ph(self):
        """ This function gets the Voltage Unbalance Factor (VUF) of the IEEE 13 nodes network.
        @:params -> None
        @:return
        vuf: dict, the Voltage Unbalance Factor (VUF) of the IEEE 13 nodes network. """

        bus_names = self.buses_names
        n_phases = 2
        for bus in bus_names:
            if self.neutral_node in list(DSSCircuit.ActiveBus(bus).Nodes):
                n_phases = 3
                break

        vuf = get_vuf_3ph(bus_names, n_phases)

        return vuf

    def get_mag_currents(self):
        """ This function gets the magnitude of the currents in the IEEE 13 nodes network.
        @:params -> None
        @:return
        currents: dict, the magnitude of the currents in the IEEE 13 nodes network. """

        lines_names = self.lines_names
        currents = get_mag_currents(lines_names)

        return currents

    @staticmethod
    def get_losses():
        """ This function gets the Losses of the system
        @:params -> None
        @:return
        losses: float, the losses in kW"""

        losses = DSSCircuit.Losses[0] / 1000
        return losses
