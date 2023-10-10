# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch
import torch.nn as nn

from batteryml.builders import MODELS
from batteryml.models.nn_model import NNModel


class MultiLayerPerceptronModule(nn.Module):
    def __init__(self,
                 in_channels: int,
                 channels: int,
                 activation: str = 'tanh',
                 dropout: float = 0.05):
        nn.Module.__init__(self)
        self.layer = nn.Linear(in_channels, channels)
        self.activation = getattr(torch, activation.lower())
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        return self.dropout(self.activation(self.layer(x)))


@MODELS.register()
class MLPRULPredictor(NNModel):
    def __init__(self,
                 in_channels: int,
                 channels: int,
                 input_height: int,
                 input_width: int,
                 dropout: float = 0.05,
                 **kwargs):
        NNModel.__init__(self, **kwargs)
        self.proj1 = nn.Sequential(
            MultiLayerPerceptronModule(input_width, channels, dropout=dropout),
            MultiLayerPerceptronModule(channels, 1, dropout=dropout))
        self.proj2 = MultiLayerPerceptronModule(in_channels, 1)
        self.proj3 = nn.Sequential(
            MultiLayerPerceptronModule(input_height, channels),
            nn.Linear(channels, 1)
        )

    def forward(self,
                feature: torch.Tensor,
                label: torch.Tensor,
                return_loss: bool = False):
        if feature.ndim == 3:
            feature = feature.unsqueeze(1)
        B, _, H, W = feature.size()
        x = feature.permute(0, 2, 1, 3).contiguous().view(B, H, -1, W)
        x = self.proj1(x).view(B, H, -1)
        x = self.proj2(x).view(B, H)
        x = self.proj3(x).view(-1)

        if return_loss:
            return torch.mean((x - label.view(-1)) ** 2)

        return x
