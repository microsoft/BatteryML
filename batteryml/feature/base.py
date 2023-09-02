# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import abc
import torch

from tqdm import tqdm
from typing import List

from batteryml.data import BatteryData


class BaseFeatureExtractor(abc.ABC):
    def __call__(self, cells: List[BatteryData]):
        pbar = tqdm(cells, desc='Extracting features')
        # features = torch.stack([self.process_cell(cell) for cell in pbar])
        features = []
        for i, cell in enumerate(pbar):
            features.append(self.process_cell(cell))
        features = torch.stack(features)
        return features.float()

    @abc.abstractmethod
    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        """Generate feature for a single cell.

        Args:
            cell_data (BatteryData): data for single cell.

        Returns:
            torch.Tensor: the processed feature.
        """
