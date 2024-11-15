# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch
import os
import json
import pickle
from batteryml.builders import LABEL_ANNOTATORS
from batteryml.data.battery_data import BatteryData

from .base import BaseLabelAnnotator


@LABEL_ANNOTATORS.register()
class SOHLabelAnnotator(BaseLabelAnnotator):
    def __init__(self,
                 cycle_index: int = 100,
                 soh_filepath: str = None,  # we'd extract soh values based on your soh file if soh_filepath was provided
                 mode: str = 'relative'
                ):
        self.cycle_index = cycle_index
        self.mode = mode
        self.soh_dict = None

        # read file
        if soh_filepath and os.path.exists(soh_filepath):
            print('read soh file')
            root, extension = os.path.splitext(soh_filepath)
            if extension == '.json':
                self.cycle_index = str(self.cycle_index)
                with open(soh_filepath, 'rb') as f:  
                    self.soh_dict = json.load(f)
            elif extension == '.pkl':
                with open(soh_filepath, 'rb') as f:
                    self.soh_dict = pickle.load(f)

    def process_cell(self, cell_data: BatteryData) -> torch.Tensor:
        cell_id = cell_data.cell_id
        if self.soh_dict:
            # if soh_filepath was provided, then use soh label in soh file
            if (cell_id not in self.soh_dict) or (self.cycle_index not in self.soh_dict[cell_id]) or (self.mode not in self.soh_dict[cell_id][self.cycle_index]):
                label = float('nan')
            else:
                label = self.soh_dict[cell_id][self.cycle_index][self.mode]
        else:
            #  if soh_filepath was not provided, the cycle data calculation is used as a fallback
            if len(cell_data.cycle_data) >= self.cycle_index:
                Qd = max(cell_data.cycle_data[self.cycle_index-1].discharge_capacity_in_Ah)
                if self.mode == 'relative':
                    nominal_capacity_in_Ah = 1
                    if hasattr(cell_data, 'nominal_capacity_in_Ah') and cell_data.nominal_capacity_in_Ah:
                        # use existed nominal_capacity_in_Ah
                        nominal_capacity_in_Ah = cell_data.nominal_capacity_in_Ah
                    else:
                        # calcute nominal_capacity_in_Ah using first cycle TODO:maybe we need to use mean of first 5 cycles to enhance stable?
                        nominal_capacity_in_Ah = max(cell_data.cycle_data[0].discharge_capacity_in_Ah)
                    label = Qd / nominal_capacity_in_Ah
                else:
                    label = Qd
            else:
                label = float('nan')
        label = torch.tensor(label)
        return label