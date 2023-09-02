# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from batteryml.builders import FEATURE_EXTRACTORS
from batteryml.data.battery_data import BatteryData
from batteryml.feature.severson import SeversonFeatureExtractor


@FEATURE_EXTRACTORS.register()
class DischargeModelFeatureExtractor(SeversonFeatureExtractor):
    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        features = [
            'Minimum', 'Variance', 'Skewness', 'Kurtosis',
            'Early discharge capacity',
            'Difference between max discharge capacity and early discharge capacity'  # noqa
        ]
        return self.get_features(cell_data, features)
