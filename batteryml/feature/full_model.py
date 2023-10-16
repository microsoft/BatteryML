# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from batteryml.builders import FEATURE_EXTRACTORS
from batteryml.data.battery_data import BatteryData
from batteryml.feature.severson import SeversonFeatureExtractor


@FEATURE_EXTRACTORS.register()
class FullModelFeatureExtractor(SeversonFeatureExtractor):
    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        features = [
            'Minimum', 'Variance',
            'Slope of linear fit to the capacity curve',
            'Intercept of linear fit to the capacity curve',
            'Early discharge capacity',
            'Average early charge time',
            'Integral of temperature over time',
            'Minimum internal resistance',
            'Internal resistance change'
        ]
        return self.get_features(cell_data, features)
