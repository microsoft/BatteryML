# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from typing import List
import numpy as np
import pandas as pd

from tqdm import tqdm
from pathlib import Path

from batteryml import BatteryData, CycleData, CyclingProtocol
from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor


@PREPROCESSORS.register()
class UL_PURPreprocessor(BasePreprocessor):
    def process(self, parentdir: str) -> List[BatteryData]:
        path = Path(parentdir)
        cells = set(
            x.stem.split('_timeseries')[0]
            for x in path.glob('*UL-PUR_N*timeseries*'))

        batteries = []
        for cell in tqdm(cells, desc='Processing UL-PUR cells'):
            timeseries_file = next(path.glob(f'*{cell}*timeseries*'))
            cycle_data_file = next(path.glob(f'*{cell}*cycle_data*'))
            timeseries_df = pd.read_csv(timeseries_file)
            cycle_data_df = pd.read_csv(cycle_data_file)
            if len(timeseries_df) == 0:
                continue
            timeseries_df, _ = clean_cell(
                timeseries_df, cycle_data_df, shifts=4)
            batteries.append(organize_cell(
                timeseries_df, cell, get_capacity(cell)))
        return batteries


def get_capacity(cell_name):
    capacity = 3.4
    if '2.5-96.5' in cell_name:  # Only charge for 94%
        capacity *= 0.94 * 3.4
    return capacity


def organize_cell(timeseries_df, name, C):
    timeseries_df = timeseries_df.sort_values('Cycle_Index')
    cycle_data = []
    for cycle_index, df in timeseries_df.groupby('Cycle_Index'):
        if cycle_index < 12:  # First 12 cycles are problematic
            continue
        cycle_data.append(CycleData(
            cycle_number=int(cycle_index - 12),
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
        form_factor='cylindrical_18650',
        anode_material='graphite',
        cathode_material='LCO',
        discharge_protocol=discharge_protocol,
        charge_protocol=charge_protocol,
        nominal_capacity_in_Ah=C,
        min_voltage_limit_in_V=2.7,
        max_voltage_limit_in_V=4.2
    )


def clean_cell(timeseries_df, cycle_data_df, shifts=2, **kwargs):
    Qd = cycle_data_df['Discharge_Capacity (Ah)'].values
    if isinstance(shifts, int):
        shifts = range(1, shifts+1)
    should_exclude = False
    for shift in shifts:
        should_exclude |= _clean_helper(Qd, shift, **kwargs)

    cycle_to_exclude = set(
        cycle_data_df[should_exclude]['Cycle_Index'].values.astype(int))
    # Also include those missing cycles into the `cycle_to_exclude`
    cycles = timeseries_df.Cycle_Index.unique()
    for cycle in range(1, int(cycles.max()+1)):
        if cycle not in cycles:
            cycle_to_exclude.add(cycle)

    cdfs, tdfs = [], []
    for cycle in cycle_to_exclude:
        imp_cycle = find_forward_imputation_cycle(cycle, cycle_to_exclude)
        if imp_cycle not in cycle_data_df.Cycle_Index.unique():
            raise ValueError(
                f'No valid imputation cycle ({cycle}->{imp_cycle})!')
        tdf = timeseries_df[timeseries_df.Cycle_Index == imp_cycle].copy()
        cdf = cycle_data_df[cycle_data_df.Cycle_Index == imp_cycle].copy()
        tdf['Cycle_Index'] = cycle
        cdf['Cycle_Index'] = cycle
        tdfs.append(tdf)
        cdfs.append(cdf)
    timeseries_df = pd.concat([
        timeseries_df[~timeseries_df.Cycle_Index.isin(cycle_to_exclude)], *tdfs
    ]).reset_index(drop=True).sort_values('Cycle_Index')
    cycle_data_df = pd.concat([
        cycle_data_df[~cycle_data_df.Cycle_Index.isin(cycle_to_exclude)], *cdfs
    ]).reset_index(drop=True).sort_values('Cycle_Index')
    return timeseries_df, cycle_data_df


def find_forward_imputation_cycle(cycle, to_exclude):
    # First look back, then look forward
    while cycle > 0 and cycle in to_exclude:
        cycle -= 1
    while cycle == 0 or cycle in to_exclude:
        cycle += 1
    return cycle


def _clean_helper(Qd, shift, **kwargs):
    diff_left = abs(Qd - np.roll(Qd, shift))
    diff_left[:shift] = np.inf
    diff_right = abs(Qd - np.roll(Qd, -shift))
    diff_right[-shift:] = np.inf
    diff = np.amin([diff_left, diff_right], 0)
    # should_exclude = find_glitches(diff, alpha)
    should_exclude = hampel_filter(diff, **kwargs)
    return should_exclude


def hampel_filter(num, ths=3):
    med = np.median(num)
    diff_with_med = abs(num - med)
    ths = np.median(diff_with_med) * ths
    return diff_with_med > ths
