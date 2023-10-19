# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import shutil
from typing import List
import zipfile
import numpy as np
import pandas as pd

from tqdm import tqdm
from numba import njit
from pathlib import Path

from batteryml import CycleData, BatteryData, CyclingProtocol
from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor


@PREPROCESSORS.register()
class RWTHPreprocessor(BasePreprocessor):
    def process(self, parentdir) -> List[BatteryData]:
        raw_file = Path(parentdir) / 'RWTH.zip'

        # Unzip the file first
        print('[INFO] Unzip the RWTH.zip file. There are '
              'many levels of compression in this dataset.',
              flush=True)
        subdir = raw_file.parent / 'RWTH-2021-04545_818642'
        if not (subdir / 'Rawdata.zip').exists():
            with zipfile.ZipFile(raw_file, 'r') as zip_ref:
                zip_ref.extractall(raw_file.parent)

        # Unzip files for all cells. We skip those begin-of-life tests.
        desc = 'Unzip RWTH files to get zip file for each cell'
        with zipfile.ZipFile(subdir / 'Rawdata.zip', 'r') as zip_ref:
            files = zip_ref.namelist()
            if not self.silent:
                files = tqdm(files, desc=desc)
            for file in files:
                if "BOL" not in file and not (subdir / file).exists():
                    zip_ref.extract(file, subdir)

        # Unzip all zip files into csv files
        datadir = subdir / 'Rohdaten'
        desc = 'Unzip the zip file of each cell'
        files = list(datadir.glob('*.zip'))
        if not self.silent:
            files = tqdm(files, desc=desc)
        for file in files:
            if not (datadir / f'{file.stem}.csv').exists():
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall(datadir)

        cells = [f'{i:03}' for i in range(2, 50)]
        if not self.silent:
            cells = tqdm(cells)
        batteries = []
        for cell in cells:
            name = f'RWTH_{cell}'
            if not self.silent:
                cells.set_description(f'Processing csv files for cell {name}')
            files = datadir.glob(f'*{cell}=ZYK*Zyk*.csv')
            df = pd.concat([pd.read_csv(f, skiprows=[1]) for f in files])
            # Sort the records by time stamp and drop the abnormal records
            df = df.drop_duplicates('Zeit').sort_values('Zeit')
            df = df[find_time_anomalies(df['Programmdauer'].values)]
            df = df.reset_index(drop=True)
            cycle_ends = find_cycle_ends(df['Strom'].values)
            # NOTE: We skip the first cycle, as the discharge stage is not complete
            cycle_ends = df['Strom'][cycle_ends].index[1:]

            cycles = []
            desc = f'Processing each cycles of cell {name}'
            for i in tqdm(range(1, len(cycle_ends)), desc=desc):
                # Process the cycle data
                cycle_data = df.iloc[cycle_ends[i-1]:cycle_ends[i]]
                V = cycle_data['Spannung'].values
                I = cycle_data['Strom'].values  # noqa
                t = cycle_data['Programmdauer'].values
                Qc = calc_Q(I, t, is_charge=True)
                Qd = calc_Q(I, t, is_charge=False)
                cycles.append(CycleData(
                    cycle_number=i,
                    voltage_in_V=V.tolist(),
                    current_in_A=I.tolist(),
                    time_in_s=t.tolist(),
                    discharge_capacity_in_Ah=Qd.tolist(),
                    charge_capacity_in_Ah=Qc.tolist()
                ))
            # Remove abnormal cycles
            Qds = np.array([max(x.discharge_capacity_in_Ah) for x in cycles])
            to_remove = remove_abnormal_cycle(Qds)
            cycles = [cycle for i, cycle in enumerate(cycles) if not to_remove[i]]
            # Organize cell
            # The nominal capacity is 2.05Ah, but due to quality issue,
            # approximately 1.85Ah each. Cycling between 20% to 80% SoC
            # makes its nominal capacity 1.85 * 0.6 = 1.11 Ah.
            # See https://publications.rwth-aachen.de/record/818642/files/Content_RWTH-2021-04545.pdf  # noqa
            batteries.append(BatteryData(
                cell_id=name,
                cycle_data=cycles,
                form_factor='cylindrical_18650',
                anode_material='graphite',
                cathode_material='NMC',
                nominal_capacity_in_Ah=1.11,  # 1.85
                charge_protocol=[
                    CyclingProtocol(
                        current_in_A=4.0,
                        start_voltage_in_V=3.5,
                        end_voltage_in_V=3.9),
                    CyclingProtocol(
                        voltage_in_V=3.9,
                        start_voltage_in_V=3.9,
                        end_soc=1.0),
                ],
                discharge_protocol=[
                    CyclingProtocol(
                        current_in_A=4.0,
                        start_voltage_in_V=3.9,
                        end_voltage_in_V=3.5),
                    CyclingProtocol(
                        voltage_in_V=3.5,
                        start_voltage_in_V=3.5,
                        end_soc=0.0),
                ],
                min_voltage_limit_in_V=3.5,
                max_voltage_limit_in_V=3.9,
                max_current_limit_in_A=4
            ))

        # Remove the extracted files
        shutil.rmtree(subdir)

        return batteries


@njit
def find_cycle_ends(current, lag=10, tolerance=0.1):
    is_cycle_end = np.zeros_like(current, dtype=np.bool8)
    enter_discharge_steps = 0
    for i in range(len(current)):
        I = current[i]  # noqa
        if i > 0 and i < len(current):
            # Process the non-smoothness
            if np.abs(current[i] - current[i-1]) > tolerance \
                    and np.abs(current[i] - current[i+1]) > tolerance:
                I = current[i+1]  # noqa
        if I < 0:  # discharge
            enter_discharge_steps += 1
        else:
            enter_discharge_steps = 0
        nms_size = 500
        if enter_discharge_steps == lag:
            t = i - lag + 1
            if t > nms_size and np.max(is_cycle_end[t-nms_size:t]) > 0:
                continue
            is_cycle_end[t] = True

    return is_cycle_end


@njit
def find_time_anomalies(time, tolerance=1e5):
    prev = time[0]
    result = np.ones_like(time, dtype=np.bool8)
    for i in range(1, len(time)):
        if time[i] - prev > tolerance:
            result[i] = False
        else:
            prev = time[i]
    return result


@njit
def remove_abnormal_cycle(Qd, eps=0.05, window=5):
    to_remove = np.zeros_like(Qd, dtype=np.bool8)
    for i in range(window, len(Qd)-window):
        prev = max(0, i - window)
        if np.abs(Qd[i] - np.median(Qd[prev:i])) > eps \
                and np.abs(Qd[i] - np.median(Qd[i:i+window])) > eps:
            to_remove[i] = True
    return to_remove


@njit
def calc_Q(I, t, is_charge):  # noqa
    Q = np.zeros_like(I)
    for i in range(1, len(I)):
        if is_charge and I[i] > 0:
            Q[i] = Q[i-1] + I[i] * (t[i] - t[i-1]) / 36e5
        elif not is_charge and I[i] < 0:
            Q[i] = Q[i-1] - I[i] * (t[i] - t[i-1]) / 36e5
        else:
            Q[i] = Q[i-1]
    return Q
