# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from batteryml.builders import LABEL_ANNOTATORS
from batteryml.data.battery_data import BatteryData

from .base import BaseLabelAnnotator


@LABEL_ANNOTATORS.register()
class RULLabelAnnotator(BaseLabelAnnotator):
    def __init__(self,
                 eol_soh: float = 0.8,
                 pad_eol: bool = True,
                 min_rul_limit: float = 100.0):
        self.eol_soh = eol_soh
        self.pad_eol = pad_eol
        self.min_rul_limit = min_rul_limit

    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        label, found_eol = 1, False
        for cycle in cell_data.cycle_data:
            label += 1
            Qd = max(cycle.discharge_capacity_in_Ah)
            if Qd <= cell_data.nominal_capacity_in_Ah * self.eol_soh:
                found_eol = True
                break

        if not found_eol:
            label = label + 1 if self.pad_eol else float('nan')

        if label <= self.min_rul_limit:
            label = float('nan')

        label = torch.tensor(label)
        return label
