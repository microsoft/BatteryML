# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import os
import re
import shutil
import zipfile
import numpy as np
import pandas as pd

from tqdm import tqdm
from numba import njit
from typing import List
from pathlib import Path
from scipy.signal import medfilt

from batteryml import BatteryData, CycleData
from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor


@PREPROCESSORS.register()
class CALCEPreprocessor(BasePreprocessor):
    def process(self, parentdir) -> List[BatteryData]:
        path = Path(parentdir)
        raw_files = [Path(f) for f in path.glob('*.zip')]
        cells = [f.stem for f in raw_files]
        if not self.silent:
            cells = tqdm(cells)
        batteries = []
        for cell, raw_file in zip(cells, raw_files):
            rawdatadir = raw_file.parent / cell
            if not rawdatadir.exists():
                if not self.silent:
                    cells.set_description(f'Inflating {cell}.zip')
                with zipfile.ZipFile(raw_file, 'r') as zip_ref:
                    zip_ref.extractall(raw_file.parent)
                if cell == 'CX2_8':
                    os.rename(
                        raw_file.parent / 'cx2_8',
                        raw_file.parent / 'CX2_8')
            if not self.silent:
                cells.set_description(f'Processing {cell} files')

            files = [
                filename for ext in ['txt', 'xlsx', 'xls']
                for filename in rawdatadir.glob(f'*.{ext}')
            ]

            if len(files) == 0:
                continue

            df = pd.concat([
                load_txt(file) if file.suffix == '.txt' else load_excel(file)
                for file in tqdm(files, desc='Load data from files')
            ])
            df = df.sort_values(['date', 'Test_Time(s)'])
            df['Cycle_Index'] = organize_cycle_index(df['Cycle_Index'].values)

            cycles = []
            for cycle_index, (_, cycle_df) in \
                    enumerate(df.groupby(['date', 'Cycle_Index'])):
                I = cycle_df['Current(A)'].values  # noqa
                t = cycle_df['Test_Time(s)'].values
                V = cycle_df['Voltage(V)'].values
                Qd = calc_Q(I, t, is_charge=False)
                Qc = calc_Q(I, t, is_charge=True)
                cycles.append(CycleData(
                    cycle_number=cycle_index,
                    voltage_in_V=V.tolist(),
                    current_in_A=I.tolist(),
                    time_in_s=t.tolist(),
                    charge_capacity_in_Ah=Qc.tolist(),
                    discharge_capacity_in_Ah=Qd.tolist()
                ))
            # Clean the cycles
            Qd = []
            for cycle_data in cycles:
                Qd.append(max(cycle_data.discharge_capacity_in_Ah))
            Qd_med = medfilt(Qd, 21)
            ths = np.median(abs(np.array(Qd) - Qd_med))
            should_keep = abs(np.array(Qd) - Qd_med) < 3 * ths
            if cell == 'CX2_34':
                should_keep[0] = False
            clean_cycles, index = [], 0
            for i in range(len(cycles)):
                if should_keep[i] and Qd[i] > 0.1:
                    index += 1
                    cycles[i].cycle_index = index
                    clean_cycles.append(cycles[i])
            # TODO: specify the charge and discharge protocols
            C = 1.1 if 'CS' in cell.upper() else 1.35

            # Skip problematic cycle
            if 'CX2_16' == cell.upper():
                clean_cycles = clean_cycles[1:]

            batteries.append(BatteryData(
                cell_id=f'CALCE_{cell}',
                form_factor='prismatic',
                anode_material='graphite',
                cathode_material='LCO',
                cycle_data=clean_cycles,
                nominal_capacity_in_Ah=C,
                max_voltage_limit_in_V=4.2,
                min_voltage_limit_in_V=2.7
            ))

            # Remove the inflated directory
            shutil.rmtree(rawdatadir)

        return batteries


@njit
def calc_Q(I, t, is_charge):  # noqa
    Q = np.zeros_like(I)
    for i in range(1, len(I)):
        if is_charge and I[i] > 0:
            Q[i] = Q[i-1] + I[i] * (t[i] - t[i-1]) / 3600
        elif not is_charge and I[i] < 0:
            Q[i] = Q[i-1] - I[i] * (t[i] - t[i-1]) / 3600
        else:
            Q[i] = Q[i-1]
    return Q


@njit
def organize_cycle_index(cycle_index):
    current_cycle, prev_value = cycle_index[0], cycle_index[0]
    for i in range(1, len(cycle_index)):
        if cycle_index[i] != prev_value:
            current_cycle += 1
            prev_value = cycle_index[i]
        cycle_index[i] = current_cycle
    return cycle_index


def extract_date_from_filename(filename):
    filename = filename.upper()
    pat = r'C[XS]2?_\d+_(\d+)_(\d+)B?_(\d+)'
    matches = re.findall(pat, filename)
    if not matches:
        pat = r'(\d+)_(\d+)_(\d+)_CX2_32'
        matches = re.findall(pat, filename)
    month, day, year = matches[0]
    month, day, year = int(month), int(day), int(year)
    return f'{year:04}-{month:02}-{day:02}'


def load_excel(excel_file):
    # Load from cache if it exists
    filename = excel_file.stem + '_cache'
    cache_file = excel_file.with_name(filename).with_suffix('.csv')
    if cache_file.exists():
        return pd.read_csv(cache_file)

    file = pd.ExcelFile(excel_file)

    channel_data = []
    for sheet_name in file.sheet_names:
        if sheet_name.startswith('Channel'):
            channel_data.append(file.parse(sheet_name))

    # Dirty data, the sheet name is Sheet1 (CX2_34_8_16_10.xlsx)
    if len(channel_data) == 0:
        for sheet_name in file.sheet_names:
            channel_data.append(file.parse(sheet_name))

    channel_data = pd.concat(channel_data)
    date = extract_date_from_filename(excel_file.stem)
    channel_data['date'] = date
    columns_to_keep = [
        'date', 'Cycle_Index', 'Test_Time(s)', 'Current(A)', 'Voltage(V)']
    df = channel_data[columns_to_keep]

    # Cache the loaded result
    df.to_csv(cache_file, index=False)

    return df


def load_txt(txt_file):
    df = pd.read_csv(txt_file, sep='\t')
    # Convert to a list of (timestamp, CycleData)
    date = extract_date_from_filename(txt_file.stem)
    result = pd.DataFrame({
        'date': date,
        'Cycle_Index': df['Charge count'] // 2 + 1,
        'Test_Time(s)': df['Time'],
        'Current(A)': df['mA'] / 1000.,
        'Voltage(V)': df['mV'] / 1000.,
    })
    return result
