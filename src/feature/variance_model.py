# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from src.builders import FEATURE_EXTRACTORS
from src.data.battery_data import BatteryData
from src.feature.severson import SeversonFeatureExtractor


@FEATURE_EXTRACTORS.register()
class VarianceModelFeatureExtractor(SeversonFeatureExtractor):
    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        return self.get_features(cell_data, ['Variance'])
