# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

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

    def process(self, parentdir: str) -> List[BatteryData]:
        """Main logic for preprocessing data."""

    def __call__(self, parentdir: str):
        batteries = self.process(parentdir)
        self.dump(batteries)
        if not self.silent:
            self.summary(batteries)

    def dump(self, batteries: List[BatteryData]):
        if not self.silent:
            batteries = tqdm(
                batteries,
                desc=f'Dump batteries to {str(self.output_dir)}')
        for battery in batteries:
            battery.dump(self.output_dir / f'{battery.cell_id}.pkl')

    def summary(self, batteries: List[BatteryData]):
        print(f'Successfully processed {len(batteries)} batteries.')
