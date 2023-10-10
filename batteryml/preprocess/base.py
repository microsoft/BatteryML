# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from pathlib import Path
from typing import Any, List
from batteryml import BatteryData
from batteryml.utils.misc import tqdm_wrapper


class BasePreprocessor:
    def __init__(self,
                 name: str,
                 output_dir: str,
                 silent: bool = False):
        self.name = name
        self.silent = silent
        self.output_dir = Path(output_dir)

    def process(self, *args, **kwargs) -> List[BatteryData]:
        """Main logic for preprocessing data."""

    def __call__(self, *args: Any, **kwargs: Any):
        batteries = self.process(*args, **kwargs)
        self.dump(batteries)
        if not self.silent:
            self.summary(batteries)

    def dump(self, batteries: List[BatteryData]):
        if not self.silent:
            batteries = tqdm_wrapper(
                batteries,
                desc=f'Dump batteries to {str(self.output_dir)}')
        for battery in batteries:
            battery.dump(self.output_dir / f'{battery.cell_id}.pkl')

    def summary(self, batteries: List[BatteryData]):
        print(f'Successfully processed {len(batteries)} batteries.')
