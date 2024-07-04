# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import os
import logging
from tqdm import tqdm
from typing import List
from pathlib import Path
from batteryml import BatteryData


class BasePreprocessor:
    def __init__(self,
                 output_dir: str,
                 silent: bool = False):
        self.silent = silent
        self.output_dir = Path(output_dir)

    def process(self, *args, **kwargs) -> List[BatteryData]:
        """Main logic for preprocessing data."""

    def __call__(self, *args, **kwargs):
        process_batteries_num, skip_batteries_num = self.process(
            *args, **kwargs)
        if not self.silent:
            print(f'Successfully processed {process_batteries_num} batteries.')
            print(f'Skip processing {skip_batteries_num} batteries.')

    def check_processed_file(self, processed_file: str):
        expected_pkl_path = os.path.join(
            self.output_dir, (f"{processed_file}.pkl"))
        if os.path.exists(expected_pkl_path) and os.path.getsize(expected_pkl_path) > 0:
            logging.info(
                f'Skip processing {processed_file}, pkl file already exists and is not empty.')
            return True
        elif os.path.exists(expected_pkl_path) and os.path.getsize(expected_pkl_path) == 0:
            logging.info(
                f'Found empty pkl file for {processed_file}.')
        return False

    # def dump(self, batteries: List[BatteryData]):
    #     if not self.silent:
    #         batteries = tqdm(
    #             batteries,
    #             desc=f'Dump batteries to {str(self.output_dir)}')
    #     for battery in batteries:
    #         battery.dump(self.output_dir / f'{battery.cell_id}.pkl')

    def dump_single_file(self, battery: BatteryData):
        battery.dump(self.output_dir / f'{battery.cell_id}.pkl')

    def summary(self, batteries: List[BatteryData]):
        print(f'Successfully processed {len(batteries)} batteries.')
