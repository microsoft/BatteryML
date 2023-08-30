# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import pickle

from typing import List


class CycleData:
    def __init__(self,
                 cycle_number: int,
                 *,
                 voltage_in_V: List[float] = None,
                 current_in_A: List[float] = None,
                 charge_capacity_in_Ah: List[float] = None,
                 discharge_capacity_in_Ah: List[float] = None,
                 time_in_s: List[float] = None,
                 temperature_in_C: List[float] = None,
                 internal_resistance_in_ohm: float = None,
                 **kwargs):
        self.cycle_number = cycle_number
        self.voltage_in_V = voltage_in_V
        self.current_in_A = current_in_A
        self.charge_capacity_in_Ah = charge_capacity_in_Ah
        self.discharge_capacity_in_Ah = discharge_capacity_in_Ah
        self.time_in_s = time_in_s
        self.temperature_in_C = temperature_in_C
        self.internal_resistance_in_ohm = internal_resistance_in_ohm

        self.additional_data = {}
        for key, val in kwargs.items():
            self.additional_data[key] = val

    def to_dict(self):
        return {
            'cycle_number': self.cycle_number,
            'current_in_A': self.current_in_A,
            'voltage_in_V': self.voltage_in_V,
            'charge_capacity_in_Ah': self.charge_capacity_in_Ah,
            'discharge_capacity_in_Ah': self.discharge_capacity_in_Ah,
            'time_in_s': self.time_in_s,
            'temperature_in_C': self.temperature_in_C,
            'internal_resistance_in_ohm': self.internal_resistance_in_ohm,
            **self.additional_data
        }


class CyclingProtocol:
    def __init__(self,
                 rate_in_C: float = None,
                 current_in_A: float = None,
                 voltage_in_V: float = None,
                 power_in_W: float = None,
                 start_voltage_in_V: str = None,
                 start_soc: float = None,
                 end_voltage_in_V: float = None,
                 end_soc: float = None):
        self.rate_in_C = rate_in_C
        self.current_in_A = current_in_A
        self.voltage_in_V = voltage_in_V
        self.power_in_W = power_in_W
        self.start_voltage_in_V = start_voltage_in_V
        self.start_soc = start_soc
        self.end_voltage_in_V = end_voltage_in_V
        self.end_soc = end_soc

    def to_dict(self):
        return {
            'rate_in_C': self.rate_in_C,
            'current_in_A': self.current_in_A,
            'voltage_in_V': self.voltage_in_V,
            'power_in_W': self.power_in_W,
            'start_voltage_in_V': self.start_voltage_in_V,
            'start_soc': self.start_soc,
            'end_voltage_in_V': self.end_voltage_in_V,
            'end_soc': self.end_soc,
        }


class BatteryData:
    def __init__(self,
                 cell_id: str,
                 *,
                 cycle_data: List[CycleData] = None,
                 form_factor: str = None,
                 anode_material: str = None,
                 cathode_material: str = None,
                 electrolyte_material: str = None,
                 nominal_capacity_in_Ah: float = None,
                 depth_of_charge: float = 1.0,
                 depth_of_discharge: float = 1.0,
                 already_spent_cycles: int = 0,
                 charge_protocol: List[CyclingProtocol] = None,
                 discharge_protocol: List[CyclingProtocol] = None,
                 max_voltage_limit_in_V: float = None,
                 min_voltage_limit_in_V: float = None,
                 max_current_limit_in_A: float = None,
                 min_current_limit_in_A: float = None,
                 reference: str = None,
                 description: str = None,
                 **kwargs):
        self.cell_id = cell_id
        self.cycle_data = cycle_data
        self.form_factor = form_factor
        self.anode_material = anode_material
        self.cathode_material = cathode_material
        self.electrolyte_material = electrolyte_material
        self.nominal_capacity_in_Ah = nominal_capacity_in_Ah
        self.depth_of_charge = depth_of_charge
        self.depth_of_discharge = depth_of_discharge
        self.already_spent_cycles = already_spent_cycles
        self.max_voltage_limit_in_V = max_voltage_limit_in_V
        self.min_voltage_limit_in_V = min_voltage_limit_in_V
        self.max_current_limit_in_A = max_current_limit_in_A
        self.min_current_limit_in_A = min_current_limit_in_A
        self.reference = reference
        self.description = description

        if isinstance(charge_protocol, CyclingProtocol):
            charge_protocol = [charge_protocol]
        self.charge_protocol = charge_protocol or []
        if isinstance(discharge_protocol, CyclingProtocol):
            discharge_protocol = [discharge_protocol]
        self.discharge_protocol = discharge_protocol or []

        for key, val in kwargs.items():
            setattr(self, key, val)

    def to_dict(self):
        result = {}
        for key, val in self.__dict__.items():
            if not callable(val) and not key.startswith('_'):
                if key == 'cycle_data' or 'protocol' in key:
                    result[key] = [cell.to_dict() for cell in val]
                elif hasattr(val, 'to_dict'):
                    result[key] = val.to_dict()
                else:
                    result[key] = val
        return result

    def dump(self, path):
        with open(path, 'wb') as fout:
            pickle.dump(self.to_dict(), fout)

    def print_description(self):
        print(f'**************description of battery cell {self.cell_id}**************')
        for key, val in self.__dict__.items():
            if key == 'cycle_data':
                print(f'cycle length: {len(val)}')
            elif val:
                print(f'{key}: {val}')

    @staticmethod
    def load(path):
        with open(path, 'rb') as fin:
            obj = pickle.load(fin)
        if obj['charge_protocol'] is not None:
            obj['charge_protocol'] = [
                CyclingProtocol(**protocol)
                for protocol in obj['charge_protocol']
            ]
        if obj['discharge_protocol'] is not None:
            obj['discharge_protocol'] = [
                CyclingProtocol(**protocol)
                for protocol in obj['discharge_protocol']
            ]
        obj['cycle_data'] = [CycleData(**data) for data in obj['cycle_data']]
        return BatteryData(**obj)
