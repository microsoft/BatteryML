# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import re
import h5py
import numpy as np

from tqdm import tqdm
from typing import List

from batteryml.builders import PREPROCESSORS
from batteryml.preprocess.base import BasePreprocessor
from batteryml import BatteryData, CycleData, CyclingProtocol


@PREPROCESSORS.register()
class MATRPreprocessor(BasePreprocessor):
    def process(self, parentdir, **kwargs) -> List[BatteryData]:
        raw_files = [
            parentdir / 'MATR_batch_20170512.mat',
            parentdir / 'MATR_batch_20170630.mat',
            parentdir / 'MATR_batch_20180412.mat',
            parentdir / 'MATR_batch_20190124.mat',
        ]

        data_batches = []
        if not self.silent:
            raw_files = tqdm(raw_files)

        for indx, f in enumerate(raw_files):
            if hasattr(raw_files, 'set_description'):
                raw_files.set_description(f'Loading {f.stem}')

            if not f.exists():
                raise FileNotFoundError(f'Batch file not found: {str(f)}')

            data_batches.append(load_batch(f, indx+1))

        batteries_num = clean_batches(
            data_batches, self.dump_single_file, self.silent)

        return batteries_num


def load_batch(file, k):
    f = h5py.File(file)
    batch = f['batch']
    num_cells = batch['summary'].shape[0]
    bat_dict = {}
    for i in tqdm(range(num_cells), desc='Processing cells', leave=False):
        cl = f[batch['cycle_life'][i, 0]][:]
        policy = f[batch['policy_readable'][i, 0]][:].tobytes()[::2].decode()
        summary_IR = np.hstack(
            f[batch['summary'][i, 0]]['IR'][0, :].tolist())
        summary_QC = np.hstack(
            f[batch['summary'][i, 0]]['QCharge'][0, :].tolist())
        summary_QD = np.hstack(
            f[batch['summary'][i, 0]]['QDischarge'][0, :].tolist())
        summary_TA = np.hstack(
            f[batch['summary'][i, 0]]['Tavg'][0, :].tolist())
        summary_TM = np.hstack(
            f[batch['summary'][i, 0]]['Tmin'][0, :].tolist())
        summary_TX = np.hstack(
            f[batch['summary'][i, 0]]['Tmax'][0, :].tolist())
        summary_CT = np.hstack(
            f[batch['summary'][i, 0]]['chargetime'][0, :].tolist())
        summary_CY = np.hstack(
            f[batch['summary'][i, 0]]['cycle'][0, :].tolist())
        summary = {
            'IR': summary_IR,
            'QC': summary_QC,
            'QD': summary_QD,
            'Tavg': summary_TA,
            'Tmin': summary_TM,
            'Tmax': summary_TX,
            'chargetime': summary_CT,
            'cycle': summary_CY
        }
        cycles = f[batch['cycles'][i, 0]]
        cycle_dict = {}
        for j in range(cycles['I'].shape[0]):
            I = np.hstack((f[cycles['I'][j, 0]][:]))  # noqa: E741
            Qc = np.hstack((f[cycles['Qc'][j, 0]][:]))
            Qd = np.hstack((f[cycles['Qd'][j, 0]][:]))
            Qdlin = np.hstack((f[cycles['Qdlin'][j, 0]][:]))
            T = np.hstack((f[cycles['T'][j, 0]][:]))
            Tdlin = np.hstack((f[cycles['Tdlin'][j, 0]][:]))
            V = np.hstack((f[cycles['V'][j, 0]][:]))
            dQdV = np.hstack((f[cycles['discharge_dQdV'][j, 0]][:]))
            t = np.hstack((f[cycles['t'][j, 0]][:]))
            cd = {
                'I': I,
                'Qc': Qc,
                'Qd': Qd,
                'Qdlin': Qdlin,
                'T': T,
                'Tdlin': Tdlin,
                'V': V,
                'dQdV': dQdV,
                't': t
            }
            cycle_dict[str(j)] = cd
        cell_dict = {
            'cycle_life': cl,
            'charge_policy': policy,
            'summary': summary,
            'cycles': cycle_dict
        }
        key = f'b{k}c' + str(i)
        bat_dict[key] = cell_dict
    return bat_dict


def clean_batches(data_batches, dump_single_file, silent):
    # remove batteries that do not reach 80% capacity
    # del data_batches[0]['b1c8']
    # del data_batches[0]['b1c10']
    # del data_batches[0]['b1c12']
    # del data_batches[0]['b1c13']
    # del data_batches[0]['b1c22']

    # There are four cells from batch1 that carried into batch2,
    # we'll remove the data from batch2 and put it with
    # the correct cell from batch1
    batch2_keys = ['b2c7', 'b2c8', 'b2c9', 'b2c15', 'b2c16']
    batch1_keys = ['b1c0', 'b1c1', 'b1c2', 'b1c3', 'b1c4']
    add_len = [662, 981, 1060, 208, 482]

    for i, bk in enumerate(batch1_keys):
        data_batches[0][bk]['cycle_life'] = \
            data_batches[0][bk]['cycle_life'] + add_len[i]
        for j in data_batches[0][bk]['summary'].keys():
            if j == 'cycle':
                data_batches[0][bk]['summary'][j] = np.hstack((
                    data_batches[0][bk]['summary'][j],
                    data_batches[1][batch2_keys[i]]['summary'][j]
                    + len(data_batches[0][bk]['summary'][j])
                ))
            else:
                data_batches[0][bk]['summary'][j] = np.hstack((
                    data_batches[0][bk]['summary'][j],
                    data_batches[1][batch2_keys[i]]['summary'][j]
                ))
        last_cycle = len(data_batches[0][bk]['cycles'].keys())
        for j, jk in enumerate(
                data_batches[1][batch2_keys[i]]['cycles'].keys()):
            data_batches[0][bk]['cycles'][str(last_cycle + j)] = \
                data_batches[1][batch2_keys[i]]['cycles'][jk]

    process_batteries_num = 0
    skip_batteries_num = 0
    for batch in data_batches:
        for cell in batch:
            if cell not in batch2_keys:
                battery = organize_cell(batch[cell], cell)
                dump_single_file(battery)
                if not silent:
                    tqdm.write(f'File: {battery.cell_id} dumped to pkl file')
                process_batteries_num += 1

    return process_batteries_num, skip_batteries_num


def organize_cell(data, name):
    cycle_data = []
    for cycle in range(len(data['cycles'])):
        if cycle == 0:
            continue
        cur_data = data['cycles'][str(cycle)]
        cycle_data.append(CycleData(
            cycle_number=cycle,
            voltage_in_V=cur_data['V'].tolist(),
            current_in_A=cur_data['I'].tolist(),
            temperature_in_C=cur_data['T'].tolist(),
            discharge_capacity_in_Ah=cur_data['Qd'].tolist(),
            charge_capacity_in_Ah=cur_data['Qc'].tolist(),
            time_in_s=cur_data['t'].tolist(),
            internal_resistance_in_ohm=data['summary']['IR'][cycle],
            Qdlin=cur_data['Qdlin'].tolist()
        ))

    # Charge and discharge protocols
    discharge_protocol = CyclingProtocol(
        rate_in_C=4.0, start_soc=1.0, end_soc=0.0
    )
    stages = [x for x in data['charge_policy'].split('-') if 'new' not in x]
    if len(stages) == 2:
        pattern = r'(.*?)C\((.*?)%\)'
        rate1, end_soc = re.findall(pattern, stages[0])[0]
        rate2 = float(stages[1][:-1] if 'C' in stages[1] else stages[1])
        charge_protocol = [
            CyclingProtocol(
                rate_in_C=float(rate1),
                start_soc=0.0,
                end_soc=float(end_soc)),
            CyclingProtocol(
                rate_in_C=float(rate2),
                start_soc=float(end_soc),
                end_soc=1.0)
        ]
    else:
        charge_protocol = [
            CyclingProtocol(
                rate_in_C=float(x),
                start_soc=i*0.2,
                end_soc=(i+1)*0.2
            ) for i, x in enumerate(stages)
        ]

    return BatteryData(
        cell_id=f'MATR_{name}',
        cycle_data=cycle_data,
        form_factor='cylindrical_18650',
        anode_material='graphite',
        cathode_material='LFP',
        discharge_protocol=discharge_protocol,
        charge_protocol=charge_protocol,
        nominal_capacity_in_Ah=1.1,
        min_voltage_limit_in_V=2.0,
        max_voltage_limit_in_V=3.5
    )
