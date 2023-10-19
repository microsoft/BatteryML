# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import pandas as pd

from tqdm import tqdm
from typing import List
from pathlib import Path

from batteryml import BatteryData, CycleData, CyclingProtocol
from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor


@PREPROCESSORS.register()
class OXPreprocessor(BasePreprocessor):
    def process(self, parentdir) -> List[BatteryData]:
        path = Path(parentdir)
        cells = set(
            x.stem.split('_timeseries')[0]
            for x in path.glob('*timeseries*'))
        batteries = []
        for cell in tqdm(cells, desc='Processing OX cells'):
            timeseries_file = next(path.glob(f'*{cell}*timeseries*'))
            timeseries_df = pd.read_csv(timeseries_file)
            # Nominal capacity is 740mAh, which leads to too short
            # cycle life. No batteries reach 0.74Ah, so we use 0.72Ah
            # to calculate the cycle life.
            # https://ora.ox.ac.uk/objects/uuid:03ba4b01-cfed-46d3-9b1a-7d4a7bdf6fac
            batteries.append(organize_cell(timeseries_df, cell, 0.72))
        return batteries


def organize_cell(timeseries_df, name, C):
    timeseries_df = timeseries_df.sort_values('Cycle_Index')
    cycle_data = []
    for cycle_index, df in timeseries_df.groupby('Cycle_Index'):
        cycle_data.append(CycleData(
            cycle_number=int(cycle_index),
            voltage_in_V=df['Voltage (V)'].tolist(),
            current_in_A=df['Current (A)'].tolist(),
            temperature_in_C=df['Cell_Temperature (C)'].tolist(),
            discharge_capacity_in_Ah=df['Discharge_Capacity (Ah)'].tolist(),
            charge_capacity_in_Ah=df['Charge_Capacity (Ah)'].tolist(),
            time_in_s=df['Test_Time (s)'].tolist()
        ))
    # Charge Protocol is constant current
    charge_protocol = [CyclingProtocol(
        rate_in_C=2.0, start_soc=0.0, end_soc=1.0
    )]
    discharge_protocol = [CyclingProtocol(
        rate_in_C=1.0, start_soc=1.0, end_soc=0.0
    )]

    return BatteryData(
        cell_id=name,
        cycle_data=cycle_data,
        form_factor='pouch',
        anode_material='graphite',
        cathode_material='LCO',
        discharge_protocol=discharge_protocol,
        charge_protocol=charge_protocol,
        nominal_capacity_in_Ah=C,
        min_voltage_limit_in_V=2.7,
        max_voltage_limit_in_V=4.2
    )
