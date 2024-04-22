""" This class contains functions to handle the analysis of IEEE 13 nodes network."""

# Import the necessary libraries and dependencies
import numpy as np
from Analysis_HC_NEV.utils.opendss_engine import *
from Analysis_HC_NEV.utils.utils_ieee13nodes import *

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

    def add_single_phase_pv_systems(self):
        """ This function adds PV systems to the IEEE 13 nodes network.
        The PV systems are added in the buses of the loads, considering if the load is single-phase and
        the connection type is wye.
        @:params -> None
        @:return -> None """

        load_names = self.load_names
        for iPV_status in range(len(load_names)):
            # Check if the PV system is already in the network
            if f'pv_{iPV_status}' not in self.pv_systems:  # TODO: Validate this condition
                DSSCircuit.SetActiveElement('load.' + str(load_names[iPV_status]))
                phases = int(DSSCircuit.ActiveCktElement.Properties('phases').Val)
                connection = DSSCircuit.ActiveCktElement.Properties('conn').Val
                kv = DSSCircuit.ActiveElement.Properties('kv').Val
                bus1 = DSSCircuit.ActiveCktElement.Properties('bus1').Val
                if phases == 1 and connection == 'wye':
                    DSSText.Command = 'new PVSystem.PV_' + str(load_names[iPV_status]) \
                                      + ' phases=1' \
                                      + ' irradiance=1' \
                                      + ' %cutin=0.05' \
                                      + ' %cutout=0.05' \
                                      + ' vmaxpu=1.5' \
                                      + ' vminpu=0.5' \
                                      + ' kva=0' \
                                      + ' pmpp=0' \
                                      + ' bus1=' + str(bus1) \
                                      + ' pf=1' \
                                      + ' enabled=false' \
                                      + f' kv= {kv}'
            else:
                print(f'PV system pv_{iPV_status} already in the network.')

        self.pv_systems = list(DSSCircuit.PVSystems.AllNames)
        if len(self.pv_systems) == 0 or self.pv_systems[0] == NONE:
            print("There were added no PV systems to the network. Please check the loads and verify if the load is "
                  "single-phase and the connection type is wye.")

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

    def get_hc_simple_by_load(
            self,
            injection: bool = True,
            kw_allocation: list = None,
            voltage_limit: list = None,
            vuf_limit: float = None,
            nev_limit: float = None,
            names_variables: list = None,
            names_limits: list = None
    ):
        """ This function calculates the Hosting Capacity (HC) of the IEEE 13 nodes network considering the injection
        ot consumption of active power in the loads.
        The method used to calculate the HC is the simple method. It is based on an iterative process to find the
        maximum power that the network can host.
        This function evaluate node by node.
        It can evaluate if the analysis is for the Injection or consumption of power.
        It considers the following possible performance indexes:
        - Voltage Unbalance Factor (VUF)
        - Voltage Deviation
        - Neutral-to-Earth Voltage (NEV) Limit
        @:params
        :param injection: bool, if True the analysis is for the injection of power, otherwise is for the consumption.
        :param kw_allocation: It is a list with the kVA values to evaluate the HC. In kVA.
        :param voltage_limit: It is a list with the voltage limits. In p.u.
        :param vuf_limit: It is the limit of the Voltage Unbalance Factor. In percentage.
        :param nev_limit: It is the limit of the Neutral-to-Earth Voltage (NEV). In Volts.
        :param names_variables: It is a list with the names of the variables to evaluate the HC.
        :param names_limits: It is a list with the names of the limits to evaluate the HC.
        @:return
        hc_results: dict, the Hosting Capacity of the IEEE 13 nodes network.
        """

        if kw_allocation is None:
            kw_allocation = [i for i in range(0, 100000, 2)]

        if names_variables is None:
            names_variables = ['HC_value', 'perfomance_limit']

        if names_limits is None:
            names_limits = ['Voltage', 'NEV', 'VUF']

        limits = {'voltage_limit': voltage_limit, 'nev_limit': nev_limit, 'vuf_limit': vuf_limit}
        load_names = filter_loads(load_names_fixed=self.load_names, n_phases=1, conn='wye')
        # temp_list = ['634a', '634b', '634c', '645', '611', '675a', '675b', '675c', '670a', '670b', '670c']
        # for i in temp_list:
        #     if i in load_names:
        #         load_names.remove(i)

        hc_results = {}  # Initialize the dictionary of results
        if len(load_names) == 0:
            print("There are no loads in the network.")
        elif any(limit is not None for limit in [voltage_limit, vuf_limit, nev_limit]):
            for load in load_names:
                self.restart_reg_controls()
                DSSSolution.Solve()
                DSSCircuit.SetActiveElement(f'load.{load}')
                original_kvar = DSSCircuit.ActiveElement.Properties('kvar').Val
                original_kw = DSSCircuit.ActiveElement.Properties('kw').Val
                # print(f"Before HC -> Load: {load} has kw: {original_kw} and kvar: {original_kvar}")
                hc_results[load] = {names_variables[0]: 0, names_variables[1]: 'None'}
                for kw in kw_allocation:
                    new_kw = -1 * kw if injection else kw
                    DSSCircuit.ActiveCktElement.Properties('kw').Val = new_kw
                    DSSCircuit.ActiveElement.Properties('kvar').Val = 0
                    DSSSolution.Solve()
                    if DSSSolution.Converged:
                        hc_temporary = self.update_hc_results(load, limits, hc_results, names_variables, names_limits)

                        if hc_temporary is not None:
                            hc_results = hc_temporary
                            break
                        else:
                            hc_results[load][names_variables[0]] = new_kw
                            hc_results[load][names_variables[1]] = 'None'
                    else:
                        print(
                            f"The circuit has not converged with kw = {new_kw} for the node {load}. "
                            f"It will enter in a loop to move the taps in the regulators.")
                        iter_count = 0
                        while not DSSSolution.Converged:
                            iter_count += 1
                            DSSSolution.Solve()
                            if DSSSolution.Converged:
                                print(f"The circuit has converged with kw = {new_kw} for the node {load} "
                                      f"after {iter_count} iterations.")
                                hc_temporary = self.update_hc_results(load, limits, hc_results, names_variables,
                                                                      names_limits)
                                if hc_temporary is not None:
                                    hc_results = hc_temporary
                                    break
                                else:
                                    hc_results[load][names_variables[0]] = new_kw
                                    hc_results[load][names_variables[1]] = 'None'
                            if iter_count > 100:
                                print(f"The circuit has not converged with kw = {new_kw} for the node {load}. "
                                      f"It will stop the iterations.")
                                break

                DSSCircuit.ActiveElement.Properties('kw').Val = original_kw
                DSSCircuit.ActiveElement.Properties('kvar').Val = original_kvar
                # print(f"After HC -> Load: {load} has kw: {DSSCircuit.ActiveElement.Properties('kw').Val}"
                #       f" and kvar: {DSSCircuit.ActiveElement.Properties('kvar').Val}")

        return hc_results

    def update_hc_results(
            self,
            load: str,
            limits: dict,
            hc_results: dict,
            names_variables: list,
            names_limits: list,
    ):
        """ This function updates the Hosting Capacity (HC) results of the IEEE 13 nodes network.
        @:params
        load: str, the name of the load to update the HC results.
        limits: dict, the limits of the IEEE 13 nodes network.
        hc_results: dict, the Hosting Capacity results of the IEEE 13 nodes network.
        names_variables: list, the names of the variables to evaluate the HC.
        names_limits: list, the names of the limits to evaluate the HC.
        @:return
        hc_results: dict, the Hosting Capacity results of the IEEE 13 nodes network."""

        voltages_pu_out_of_range, voltages_nev_out_of_range, vuf_out_of_range = self.validate_limits(limits)
        voltage_limit = limits['voltage_limit']
        nev_limit = limits['nev_limit']
        vuf_limit = limits['vuf_limit']
        if voltage_limit is not None and any(value for value in voltages_pu_out_of_range.values()):
            hc_results[load][names_variables[1]] = names_limits[0]
            return hc_results
        elif nev_limit is not None and any(value for value in voltages_nev_out_of_range.values()):
            hc_results[load][names_variables[1]] = names_limits[1]
            return hc_results
        elif vuf_limit is not None and vuf_out_of_range:
            hc_results[load][names_variables[1]] = names_limits[2]
            return hc_results
        else:
            return None

    def validate_limits(self, limits: dict):
        """ This function validates the limits of the IEEE 13 nodes network.
        @:params
        limits: dict, the limits of the IEEE 13 nodes network.
        @:return
        voltages_pu_out_of_range: dict, the values of the voltages in per unit out of range
        voltages_nev_out_of_range: dict, the values of the voltages out of range
        vuf_out_of_range: dict, the values of the voltage unbalance factor out of range"""

        voltages_pu_out_of_range = {}
        voltages_nev_out_of_range = {}
        vuf_out_of_range = {}
        # Get the values for the assessment
        voltages_pu, voltages, vuf = self.get_values_assessment_hc()
        del voltages_pu['n']
        del voltages['a']
        del voltages['b']
        del voltages['c']

        voltage_limit = limits['voltage_limit']
        nev_limit = limits['nev_limit']
        vuf_limit = limits['vuf_limit']

        if voltage_limit is not None:
            voltages_pu_out_of_range = {
                key: any((value < voltage_limit[0] or value > voltage_limit[1]) for value in values) for
                key, values in voltages_pu.items()}

        if nev_limit is not None:
            voltages_nev_out_of_range = {key: any((value > nev_limit) for value in values) for
                                         key, values
                                         in
                                         voltages.items()}

        if vuf_limit is not None:
            vuf_out_of_range = any(value > vuf_limit for value in vuf.values() if not np.isnan(value))

        return voltages_pu_out_of_range, voltages_nev_out_of_range, vuf_out_of_range

    def get_values_assessment_hc(self):
        """ This function calculate the values for the HC assessment
        @:params -> None
        @:return
        voltages_pu_per_node: dict, the values of the voltages in each bus in per unit
        voltages_per_node: dict, the values of the voltage in each bus in Volts
        vuf: dict, the values of the voltage unbalance factor in percentage"""

        buses_names = self.buses_names
        mag_voltages_pu = get_mag_voltages(bus_names=buses_names, mag_pu=True, show_message=False)
        mag_voltages = get_mag_voltages(bus_names=buses_names, mag_pu=False, show_message=False)
        n_phases = 3 if self.has_neutral else 2
        vuf = get_vuf_3ph(buses_names, n_phases)

        # Getting the voltages per node
        voltages_pu_per_node = {node: [
            np.nan if node not in mag_voltages_pu[bus] or mag_voltages_pu[bus][node] == 0 else mag_voltages_pu[bus][
                node] for bus in buses_names] for node in NODES_NAME}
        voltages_per_node = {
            node: [np.nan if node not in mag_voltages[bus] else mag_voltages[bus][node] for bus in buses_names] for node
            in NODES_NAME}

        return voltages_pu_per_node, voltages_per_node, vuf
