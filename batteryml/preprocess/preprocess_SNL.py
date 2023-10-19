# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import numpy as np
import pandas as pd

from tqdm import tqdm
from typing import List
from pathlib import Path

from batteryml import BatteryData, CycleData, CyclingProtocol
from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor


@PREPROCESSORS.register()
class SNLPreprocessor(BasePreprocessor):
    def process(self, parentdir) -> List[BatteryData]:
        path = Path(parentdir)
        cells = set(
            x.stem.split('_timeseries')[0]
            for x in path.glob('*timeseries*'))
        to_drop = [
            'SNL_18650_NMC_25C_20-80_0.5-0.5C_d',
            'SNL_18650_LFP_25C_20-80_0.5-3C_a',
            'SNL_18650_NMC_25C_20-80_0.5-0.5C_a',
            'SNL_18650_LFP_25C_40-60_0.5-3C_b',
            'SNL_18650_NMC_25C_40-60_0.5-0.5C_a',
            'SNL_18650_LFP_25C_40-60_0.5-3C_a',
            'SNL_18650_NMC_25C_40-60_0.5-0.5C_b',
            'SNL_18650_LFP_15C_0-100_0.5-1C_a',
            'SNL_18650_LFP_25C_20-80_0.5-0.5C_b',
            'SNL_18650_LFP_15C_0-100_0.5-1C_b',
            'SNL_18650_NMC_25C_20-80_0.5-3C_a',
            'SNL_18650_LFP_15C_0-100_0.5-2C_a',
            'SNL_18650_LFP_25C_40-60_0.5-0.5C_b',
            'SNL_18650_LFP_25C_20-80_0.5-0.5C_c',
            'SNL_18650_LFP_25C_40-60_0.5-0.5C_a',
            'SNL_18650_LFP_25C_20-80_0.5-0.5C_d',
            'SNL_18650_LFP_25C_20-80_0.5-0.5C_a',
            'SNL_18650_NMC_25C_0-100_0.5-0.5C_a',
            'SNL_18650_NCA_25C_40-60_0.5-0.5C_a',
            'SNL_18650_NMC_25C_40-60_0.5-3C_a',
            'SNL_18650_NMC_25C_20-80_0.5-0.5C_b',
            'SNL_18650_NMC_25C_40-60_0.5-3C_b',
            'SNL_18650_NMC_25C_20-80_0.5-0.5C_c',
            'SNL_18650_NCA_25C_40-60_0.5-0.5C_b',
            'SNL_18650_NMC_25C_20-80_0.5-3C_b']
        cells = tuple(cell for cell in cells if cell not in to_drop)
        batteries = []
        for cell in tqdm(cells, desc='Processing SNL cells'):
            timeseries_file = next(path.glob(f'*{cell}*timeseries*'))
            cycle_data_file = next(path.glob(f'*{cell}*cycle_data*'))
            timeseries_df = pd.read_csv(timeseries_file)
            cycle_data_df = pd.read_csv(cycle_data_file)
            if cell == 'SNL_18650_NCA_25C_0-100_0.5-0.5C_a':
                se = cycle_data_df['Discharge_Capacity (Ah)'].values < 1.5
            else:
                se = False
            timeseries_df, cycle_data_df = clean_snl_cell(
                timeseries_df, cycle_data_df, should_exclude=se)
            batteries.append(organize_cell(timeseries_df, cell))
        return batteries


def get_capacity(cell_name):
    if 'NMC' in cell_name:
        if '15C' in cell_name:
            return 3 * 0.9
        return 3
    if 'NCA' in cell_name:
        if '20-80' in cell_name:  # Only use 60% of the capacity
            return 1.92  # 3.2 * 0.6
        if '15C' in cell_name:  # Low temperature compromise
            return 3.2 * 0.9
        return 3.2
    return 1.1


def organize_cell(timeseries_df, name):
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
    rates = name.split('_')[-2][:-1].split('-')
    charge_protocol = [CyclingProtocol(
        rate_in_C=float(rates[0]),
        start_soc=0.0,
        end_soc=1.0
    )]
    discharge_protocol = [CyclingProtocol(
        rate_in_C=float(rates[1]),
        start_soc=1.0,
        end_soc=0.0
    )]

    # Operating bounds
    cathode = name.split('_')[2]
    min_voltage_in_V = 2.5 if cathode == 'NCA' else 2.0
    max_voltage_in_V = 3.6 if cathode == 'LFP' else 4.2
    max_current_in_A = 30.0 if cathode == 'LFP' else \
        (6.0 if cathode == 'NCA' else 20.0)

    C = get_capacity(name)

    return BatteryData(
        cell_id=name,
        cycle_data=cycle_data,
        form_factor='cylindrical_18650',
        anode_material='graphite',
        cathode_material=cathode,
        discharge_protocol=discharge_protocol,
        charge_protocol=charge_protocol,
        nominal_capacity_in_Ah=C,
        max_current_limit_in_A=max_current_in_A,
        min_voltage_limit_in_V=min_voltage_in_V,
        max_voltage_limit_in_V=max_voltage_in_V
    )


def find_forward_imputation_cycle(cycle, to_exclude):
    # First look back, then look forward
    while cycle > 0 and cycle in to_exclude:
        cycle -= 1
    while cycle == 0 or cycle in to_exclude:
        cycle += 1
    return cycle


def clean_snl_cell(
    timeseries_df, cycle_data_df,
    should_exclude=False, shifts=2, ths=10
):
    Qd = cycle_data_df['Discharge_Capacity (Ah)'].values
    for shift in range(1, shifts+1):
        diff_left = abs(Qd - np.roll(Qd, shift))
        diff_left[:shift] = np.inf
        diff_right = abs(Qd - np.roll(Qd, -shift))
        diff_right[-shift:] = np.inf
        diff = np.amin([diff_left, diff_right], 0)
        med = np.median(diff[diff > 0])
        should_exclude |= diff > med * ths

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
    ]).sort_values('Cycle_Index').reset_index(drop=True)
    cycle_data_df = pd.concat([
        cycle_data_df[~cycle_data_df.Cycle_Index.isin(cycle_to_exclude)], *cdfs
    ]).sort_values('Cycle_Index').reset_index(drop=True)
    return timeseries_df, cycle_data_df
