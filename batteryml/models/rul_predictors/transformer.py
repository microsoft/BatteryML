# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch
import torch.nn as nn

from batteryml.builders import MODELS
from batteryml.models.nn_model import NNModel


@MODELS.register()
class TransformerRULPredictor(NNModel):
    def __init__(self,
                 in_channels,
                 channels,
                 input_height,
                 input_width,
                 num_layers=2,
                 nhead=4,
                 **kwargs):
        NNModel.__init__(self, **kwargs)
        self.proj = nn.Linear(in_channels * input_width, channels)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=channels,
            nhead=nhead,
            dim_feedforward=channels,
            batch_first=True)
        self.transformer = nn.TransformerDecoder(decoder_layer, num_layers)
        self.fc = nn.Linear(channels * input_height, 1)

    def forward(self,
                feature: torch.Tensor,
                label: torch.Tensor,
                return_loss: bool = False):
        print(feature.shape)
        if feature.ndim == 4:
            B, C, N, L = feature.shape
            feature = feature.transpose(1, 2).contiguous().view(B, N, -1)
        elif feature.ndim == 3:
            B, N, _ = feature.shape
        input_ = self.proj(feature)
        embedding = self.transformer(input_, input_).view(B, -1)
        pred = self.fc(embedding).view(-1)

        if return_loss:
            return torch.mean((pred - label.view(-1)) ** 2)

        return pred