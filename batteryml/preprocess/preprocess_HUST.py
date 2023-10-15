# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import shutil
import pickle
import zipfile
import numpy as np

from tqdm import tqdm
from numba import njit
from typing import List
from pathlib import Path

from batteryml import CycleData, BatteryData, CyclingProtocol
from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor


@PREPROCESSORS.register()
class HUSTPreprocessor(BasePreprocessor):
    def process(self, parentdir) -> List[BatteryData]:
        raw_file = Path(parentdir) / 'hust_data.zip'

        with zipfile.ZipFile(raw_file, 'r') as zip_ref:
            pbar = zip_ref.namelist()
            if not self.silent:
                pbar = tqdm(pbar)
            for file in pbar:
                if not self.silent:
                    pbar.set_description(f'Unzip HUST file {file}')
                zip_ref.extract(file, raw_file.parent)

        datadir = raw_file.parent / 'our_data'
        cell_files = list(datadir.glob('*.pkl'))
        if not self.silent:
            cell_files = tqdm(
                cell_files, desc='Processing HUST cells')
        batteries = []
        for cell_file in cell_files:
            cell_id = cell_file.stem
            cell_name = f'HUST_{cell_id}'
            with open(cell_file, 'rb') as fin:
                cell_data = pickle.load(fin)[cell_id]['data']
            cycles = []
            for cycle in range(len(cell_data)):
                df = cell_data[cycle+1]
                I = df['Current (mA)'].values / 1000.  # noqa
                t = df['Time (s)'].values
                V = df['Voltage (V)'].values
                Qd = calc_Q(I, t, is_charge=False)
                Qc = calc_Q(I, t, is_charge=True)
                cycles.append(CycleData(
                    cycle_number=cycle+1,
                    voltage_in_V=V.tolist(),
                    current_in_A=I.tolist(),
                    time_in_s=t.tolist(),
                    discharge_capacity_in_Ah=Qd.tolist(),
                    charge_capacity_in_Ah=Qc.tolist()
                ))

            rates = DISCHARGE_RATES[cell_id]
            # Skip first problematic cycles
            if cell_name == 'HUST_7-5':
                cycles = cycles[2:]
            batteries.append(BatteryData(
                cell_id=cell_name,
                cycle_data=cycles,
                form_factor='cylindrical_18650',
                anode_material='graphite',
                cathode_material='LFP',
                nominal_capacity_in_Ah=1.1,
                charge_protocol=[
                    CyclingProtocol(
                        rate_in_C=5.0,
                        start_soc=0.0,
                        end_soc=0.8),
                    CyclingProtocol(
                        rate_in_C=1.0,
                        start_soc=0.8,
                        end_voltage_in_V=3.6),
                    CyclingProtocol(
                        voltage_in_V=3.6,
                        start_voltage_in_V=3.6,
                        end_soc=1.0)
                ],
                discharge_protocol=[
                    CyclingProtocol(
                        rate_in_C=float(rates[0]),
                        start_soc=1.0,
                        end_soc=0.6),
                    CyclingProtocol(
                        rate_in_C=float(rates[1]),
                        start_soc=0.6,
                        end_soc=0.4),
                    CyclingProtocol(
                        rate_in_C=float(rates[2]),
                        start_soc=0.4,
                        end_soc=0.2),
                    CyclingProtocol(
                        rate_in_C=1.0,
                        start_soc=0.2,
                        end_voltage_in_V=2.0),
                ],
                min_voltage_limit_in_V=2.0,
                max_voltage_limit_in_V=3.6
            ))

        # Remove the inflated data
        shutil.rmtree(datadir)

        return batteries


# See https://www.rsc.org/suppdata/d2/ee/d2ee01676a/d2ee01676a1.pdf
DISCHARGE_RATES = {
    '1-1': [5, 1, 1],
    '1-2': [5, 1, 2],
    '1-3': [5, 1, 3],
    '1-4': [5, 1, 4],
    '1-5': [5, 1, 5],
    '1-6': [5, 2, 1],
    '1-7': [5, 2, 2],
    '1-8': [5, 2, 3],
    '2-2': [5, 2, 5],
    '2-3': [5, 3, 1],
    '2-4': [5, 3, 2],
    '2-5': [5, 3, 3],
    '2-6': [5, 3, 4],
    '2-7': [5, 3, 5],
    '2-8': [5, 4, 1],
    '3-1': [5, 4, 2],
    '3-2': [5, 4, 3],
    '3-3': [5, 4, 4],
    '3-4': [5, 4, 5],
    '3-5': [5, 5, 1],
    '3-6': [5, 5, 2],
    '3-7': [5, 5, 3],
    '3-8': [5, 5, 4],
    '4-1': [5, 5, 5],
    '4-2': [4, 1, 1],
    '4-3': [4, 1, 2],
    '4-4': [4, 1, 3],
    '4-5': [4, 1, 4],
    '4-6': [4, 1, 5],
    '4-7': [4, 2, 1],
    '4-8': [4, 2, 2],
    '5-1': [4, 2, 3],
    '5-2': [4, 2, 4],
    '5-3': [4, 2, 5],
    '5-4': [4, 3, 1],
    '5-5': [4, 3, 2],
    '5-6': [4, 3, 3],
    '5-7': [4, 3, 4],
    '6-1': [4, 4, 1],
    '6-2': [4, 4, 2],
    '6-3': [4, 4, 3],
    '6-4': [4, 4, 4],
    '6-5': [4, 4, 5],
    '6-6': [4, 5, 1],
    '6-8': [4, 5, 3],
    '7-1': [4, 5, 4],
    '7-2': [4, 5, 5],
    '7-3': [3, 1, 1],
    '7-4': [3, 1, 2],
    '7-5': [3, 1, 3],
    '7-6': [3, 1, 4],
    '7-7': [3, 1, 5],
    '7-8': [3, 2, 1],
    '8-1': [3, 2, 2],
    '8-2': [3, 2, 3],
    '8-3': [3, 2, 4],
    '8-4': [3, 2, 5],
    '8-5': [3, 3, 1],
    '8-6': [3, 3, 2],
    '8-7': [3, 3, 3],
    '8-8': [3, 3, 4],
    '9-1': [3, 3, 5],
    '9-2': [3, 4, 1],
    '9-3': [3, 4, 2],
    '9-4': [3, 4, 3],
    '9-5': [3, 4, 4],
    '9-6': [3, 4, 5],
    '9-7': [3, 5, 1],
    '9-8': [3, 5, 2],
    '10-1': [3, 5, 3],
    '10-2': [3, 5, 4],
    '10-3': [3, 5, 5],
    '10-4': [2, 4, 1],
    '10-5': [2, 5, 2],
    '10-6': [2, 3, 3],
    '10-7': [2, 2, 4],
    '10-8': [2, 1, 5],
}


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
