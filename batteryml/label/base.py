# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import abc
import torch
from typing import List

from batteryml.data.battery_data import BatteryData


class BaseLabelAnnotator(abc.ABC):
    def __call__(self, cells: List[BatteryData]):
        return torch.stack([
            self.process_cell(cell) for cell in cells]).float().view(-1)

    @abc.abstractmethod
    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        """Generate label for a single cell.

        Args:
            cell_data (BatteryData): data for single cell.

        Returns:
            torch.Tensor: the processed label.
        """
