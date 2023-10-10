# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch
import torch.nn as nn

from batteryml.builders import MODELS
from batteryml.models.nn_model import NNModel


@MODELS.register()
class LSTMRULPredictor(NNModel):
    def __init__(self,
                 in_channels: int,
                 channels: int,
                 input_height: int,
                 input_width: int,
                 **kwargs):
        NNModel.__init__(self, **kwargs)
        self.lstm = nn.LSTM(
            in_channels * input_width, channels, 2, batch_first=True)
        self.fc = nn.Linear(channels, 1)

    def forward(self,
                feature: torch.Tensor,
                label: torch.Tensor,
                return_loss: bool = False):
        if feature.ndim == 3:
            feature = feature.unsqueeze(1)
        B, _, H, _ = feature.size()
        x = feature.permute(0, 2, 1, 3).contiguous().view(B, H, -1)
        x, _ = self.lstm(x)
        x = x[:, -1].contiguous().view(B, -1)
        x = self.fc(x).view(-1)

        if return_loss:
            return torch.mean((x - label.view(-1)) ** 2)

        return x
