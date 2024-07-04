# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import os
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from typing import List
from pathlib import Path

from batteryml.builders import PREPROCESSORS
from batteryml.utils import import_config
from batteryml.preprocess.base import BasePreprocessor
from batteryml import BatteryData, CycleData, CyclingProtocol


@PREPROCESSORS.register()
class NEWAREPreprocessor(BasePreprocessor):
    def process(self, parentdir, config_path, **kwargs) -> List[BatteryData]:
        if config_path is None or str(config_path) == "None":
            raise ValueError("Config path is not specified.")
        else:
            CONFIG_FIELDS = ["column_names", "data_types", "scales"]
            CONVERSION_CONFIG = import_config(Path(config_path), CONFIG_FIELDS)

        cell_files = [f for f in Path(parentdir).iterdir(
        ) if f.is_file() and not f.name.endswith('.yaml')]

        if not self.silent:
            cell_files = tqdm(
                cell_files, desc='Processing data from NEWARE cycler')

        process_batteries_num = 0
        skip_batteries_num = 0
        for cell_file in cell_files:
            whether_to_skip = self.check_processed_file(
                "NEWARE_"+cell_file.stem)
            if whether_to_skip == True:
                skip_batteries_num += 1
                continue

            logging.info(f'Processing cell_file: {cell_file.name}')

            battery = organize_cell_file(cell_file, CONVERSION_CONFIG)
            self.dump_single_file(battery)
            process_batteries_num += 1

            if not self.silent:
                logging.info(f'File: {battery.cell_id} dumped to pkl file')

        return process_batteries_num, skip_batteries_num


def organize_cell_file(cell_file, CONVERSION_CONFIG):
    ir_column_name = '"DCIR(O)"'

    record_data = []
    with open(cell_file, encoding="ISO-8859-1") as input:
        cycle_header = input.readline().replace("\t", "")
        step_header = input.readline().replace("\t", "")
        ir_index = step_header.split(",").index(ir_column_name)
        record_header = input.readline().replace("\t", "").split(",")
        record_header[0] = cycle_header.split(",")[0]
        record_header[1] = step_header.split(",")[1]
        record_header[22] = ir_column_name
        record_header = ",".join(record_header)
        record_header = record_header.encode("ascii", "ignore").decode()

        cycle_number = 0
        step_number = 0
        ir_value = None
        for line in input:
            if line[:2] == r',"':  # step data
                step_number = line.split(",")[1]
                ir_value = line.split(",")[ir_index]
            elif line[:2] == r",,":  # record data
                line_list = line.split(",")
                line_list[0] = cycle_number
                line_list[1] = step_number
                line_list[22] = ir_value
                record_data.append(line_list)
            else:  # cycle data
                cycle_number = line.split(",")[0]

    cleaned_columns = [col.replace('"', '')
                       for col in record_header.split(",")]
    record_df = pd.DataFrame(record_data, columns=cleaned_columns)
    record_df = record_df.replace({'\t': '', '"': ''}, regex=True)

    data = record_df.loc[:, ~record_df.columns.str.contains("Unnamed")]

    data["Time(h:min:s.ms)"] = data["Time(h:min:s.ms)"].apply(
        lambda x: 3600 * float(x.split(":")[-3]) + 60 * float(x.split(":")[-2]) + float(x.split(":")[-1]))

    # Deal with missing data in the internal resistance
    data["DCIR(O)"] = data["DCIR(O)"].apply(
        lambda x: np.nan if x == "-" else x
    )

    columns = {
        v: k for k, v in CONVERSION_CONFIG["column_names"].items() if v in data.columns}
    data.rename(columns=columns, inplace=True)

    data_types = {
        k: v for k, v in CONVERSION_CONFIG["data_types"].items() if k in data.columns}
    data = data.astype(data_types)

    scales = {k: v for k,
              v in CONVERSION_CONFIG["scales"].items() if k in data.columns}
    for column, scale in scales.items():
        data[column] *= scale

    data["internal_resistance"] = data["internal_resistance"].ffill()
    data["internal_resistance"] = data["internal_resistance"].bfill()

    data["test_time"] = (
        data["step_time"].diff().fillna(0).apply(
            lambda x: 0 if x < 0 else x).cumsum()
    )

    cycles = data_cycles(data)

    metadata_file_path = cell_file.with_suffix('.metadata.yaml')
    metadata_file = metadata_file_path if os.path.exists(
        metadata_file_path) else None
    metadata = organize_metadata(metadata_file)

    return organize_cell(cell_file.stem, cycles, metadata)


def data_cycles(raw_data):
    grouped_by_cycle_idx = raw_data.groupby('cycle_index')
    columns_to_group_mapping = {
        'data_point': 'data_point',
        'step_index': 'step_index',
        'current': 'I',
        'voltage': 'V',
        'charge_capacity': 'Qc',
        'discharge_capacity': 'Qd',
        'charge_energy': 'Ec',
        'discharge_energy': 'Ed',
        'temperature': 'T',
        'internal_resistance': 'IR',
        'test_time': 't',
        'date_time': 'date_time_iso',
    }
    grouped_data = {}
    grouped_data['data_point'] = grouped_by_cycle_idx.apply(
        lambda x: (x.index + 1 - x.index[0]).tolist()
    )
    for column in columns_to_group_mapping.keys():
        if column in raw_data.columns:
            try:
                grouped_data[column] = grouped_by_cycle_idx[column].apply(list)
            except Exception as e:
                logging.warning(
                    f'Failed to process column {column} to group: {e}')
        else:
            grouped_data[column] = grouped_by_cycle_idx.apply(
                lambda x: [None]*len(x))

    cycle_dict = {}
    all_cycles = set(range(max(grouped_by_cycle_idx.groups.keys()) + 1))
    existing_cycles = set(grouped_by_cycle_idx.groups.keys())

    missing_cycles = all_cycles - existing_cycles
    for missing_cycle in missing_cycles:
        logging.warning(f"Data of cycle {missing_cycle} missed.")

    for cdi, i in enumerate(grouped_by_cycle_idx.groups.keys()):
        cd = {}
        try:
            cd['data_point'] = grouped_data['data_point'][i]
            for field in columns_to_group_mapping.keys():
                if field == 'internal_resistance':
                    #####################################################################
                    # Assume the last IR of each cycle is representative of that cycle. #
                    #####################################################################
                    cd['IR'] = grouped_data[field][i][-1]
                elif field == 'test_time':
                    min_date_time = min(grouped_data[field][i])
                    cd['t'] = [
                        time - min_date_time for time in grouped_data[field][i]]
                else:
                    cd[columns_to_group_mapping[field]] = grouped_data[field][i]
        except Exception as e:
            logging.warning(
                f"Error processing field '{field}' in cycle {i}")
        cycle_dict[str(cdi)] = cd

    return cycle_dict


# Need adjusting to custom metadata
def organize_metadata(meta_path):
    METADATA_CONFIG_FIELDS = ["form_factor", "anode_material", "cathode_material",
                              "nominal_capacity_in_Ah",
                              "min_voltage_limit_in_V", "max_voltage_limit_in_V",
                              "charge_protocol", "discharge_protocol"]
    METADATA_CONFIG = {field: None for field in METADATA_CONFIG_FIELDS}

    try:
        if meta_path is None or str(meta_path) == "None":
            raise ValueError("Metadata config path is not specified.")
        config = import_config(Path(meta_path), METADATA_CONFIG_FIELDS)
        METADATA_CONFIG.update(config)
    except (ValueError, FileNotFoundError) as e:
        logging.error(e)

    charge_protocols = [CyclingProtocol(
        **cp) for cp in METADATA_CONFIG.get('charge_protocol', []) or []]
    discharge_protocols = [CyclingProtocol(
        **dp) for dp in METADATA_CONFIG.get('discharge_protocol', []) or []]

    metadata = {
        "form_factor": METADATA_CONFIG.get("form_factor"),
        "anode_material": METADATA_CONFIG.get("anode_material"),
        "cathode_material": METADATA_CONFIG.get("cathode_material"),
        "charge_protocol": charge_protocols,
        "discharge_protocol": discharge_protocols,
        "nominal_capacity_in_Ah": METADATA_CONFIG.get("nominal_capacity_in_Ah"),
        "min_voltage_limit_in_V": METADATA_CONFIG.get("min_voltage_limit_in_V"),
        "max_voltage_limit_in_V": METADATA_CONFIG.get("max_voltage_limit_in_V")
    }
    return metadata


def organize_cell(name, cycles, metadata):
    cycle_data = []
    for cycle_idx, cycle in cycles.items():
        # Skip the first cycle if it is necessary
        # if int(cycle_idx) == 0:
        #     continue
        cycle_data.append(CycleData(
            cycle_number=cycle_idx,
            voltage_in_V=cycle['V'],
            current_in_A=cycle['I'],
            charge_capacity_in_Ah=cycle['Qc'],
            discharge_capacity_in_Ah=cycle['Qd'],
            time_in_s=cycle['t'],
            temperature_in_C=cycle['T'],
            internal_resistance_in_ohm=cycle['IR'],

            energy_charge=cycle['Ec'],
            energy_discharge=cycle['Ed'],
            step_index=cycle['step_index'],
            data_point=cycle['data_point']
        ))

    return BatteryData(
        cell_id=f'NEWARE_{name}',
        cycle_data=cycle_data,
        form_factor=metadata["form_factor"],
        anode_material=metadata["anode_material"],
        cathode_material=metadata["cathode_material"],
        charge_protocol=metadata["charge_protocol"],
        discharge_protocol=metadata["discharge_protocol"],
        nominal_capacity_in_Ah=metadata["nominal_capacity_in_Ah"],
        min_voltage_limit_in_V=metadata["min_voltage_limit_in_V"],
        max_voltage_limit_in_V=metadata["max_voltage_limit_in_V"]
    )
