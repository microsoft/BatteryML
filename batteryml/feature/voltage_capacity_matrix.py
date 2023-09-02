# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from typing import List

from batteryml.builders import FEATURE_EXTRACTORS
from batteryml.data.battery_data import BatteryData
from batteryml.feature.base import BaseFeatureExtractor
from batteryml.feature.severson import get_Qdlin, smooth


@FEATURE_EXTRACTORS.register()
class VoltageCapacityMatrixFeatureExtractor(BaseFeatureExtractor):
    def __init__(self,
                 interp_dim: int = 1000,
                 diff_base: int = 9,
                 cycles_to_keep: List[int] = None,
                 min_cycle_index: int = 0,
                 max_cycle_index: int = 99,
                 use_precalculated_qdlin: bool = False,
                 smooth: bool = True,
                 cycle_average: int = None):
        self.interp_dim = interp_dim
        self.min_cycle_index = min_cycle_index
        self.max_cycle_index = max_cycle_index
        self.use_precalculated_qdlin = use_precalculated_qdlin

        assert diff_base <= max_cycle_index, (diff_base, max_cycle_index)
        assert diff_base >= min_cycle_index, (diff_base, min_cycle_index)
        self.diff_base = diff_base

        if cycles_to_keep is not None and isinstance(cycles_to_keep, int):
            cycles_to_keep = [cycles_to_keep]
        self.cycles_to_keep = cycles_to_keep

        self.smooth = smooth

        # See https://github.com/petermattia/revisit-severson-et-al/blob/main/revisit-severson-et-al.ipynb noqa
        self.cycle_average = cycle_average

    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        feature = []
        diff_base_qdlin = get_Qdlin(
            cell_data,
            cell_data.cycle_data[self.diff_base],
            self.use_precalculated_qdlin)
        if self.smooth:
            diff_base_qdlin = smooth(diff_base_qdlin)
        if self.cycle_average is not None:
            diff_base_qdlin = diff_base_qdlin[..., ::self.cycle_average]

        for cycle_index, cycle_data in enumerate(cell_data.cycle_data):
            if cycle_index < self.min_cycle_index:
                continue
            if cycle_index > self.max_cycle_index:
                break

            if self.cycles_to_keep is not None \
                    and cycle_index not in self.cycles_to_keep:
                continue

            qdlin = get_Qdlin(
                cell_data, cycle_data, self.use_precalculated_qdlin)
            if self.smooth:
                qdlin = smooth(qdlin)
            if self.cycle_average is not None:
                qdlin = qdlin[..., ::self.cycle_average]

            diff_qdlin = qdlin - diff_base_qdlin
            if self.smooth:
                diff_qdlin = smooth(diff_qdlin)

            feature.append(torch.from_numpy(diff_qdlin))
        feature = torch.stack(feature)

        # Fill NaN
        feature[torch.isnan(feature) | torch.isinf(feature)] = 0.

        return feature