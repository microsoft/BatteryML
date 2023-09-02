# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch
import torch.nn as nn

from batteryml.builders import MODELS
from batteryml.models.nn_model import NNModel


class BatteryDropout(nn.Module):
    def __init__(self, ratio: float = 0.1):
        nn.Module.__init__(self)
        self.ratio = ratio

    def forward(self, x):
        # 1/2 probability to drop the cycles
        # 1/2 probability to drop a segment of the signals
        pass


class ConvModule(nn.Module):
    def __init__(self, din, dout, kernel_size,
                 act_fn: str = 'relu',
                 dropout: float = 0.1):
        nn.Module.__init__(self)
        self.kernel_size = kernel_size
        self.conv1 = nn.Conv2d(din, dout, kernel_size)
        self.pool1 = nn.AvgPool2d(kernel_size)
        self.conv2 = nn.Conv2d(dout, dout, kernel_size)
        self.pool2 = nn.AvgPool2d(kernel_size)
        self.act_fn = getattr(torch, act_fn)
        self.dropout = nn.Dropout2d(dropout)

    def output_shape(self, H, W):
        # conv1 output
        H, W = H - self.kernel_size[0] + 1, W - self.kernel_size[1] + 1
        # pool1 output
        H = int((H - self.kernel_size[0]) / self.kernel_size[0] + 1)
        W = int((W - self.kernel_size[1]) / self.kernel_size[1] + 1)
        # conv2 output
        H, W = H - self.kernel_size[0] + 1, W - self.kernel_size[1] + 1
        # pool2 output
        H = int((H - self.kernel_size[0]) / self.kernel_size[0] + 1)
        W = int((W - self.kernel_size[1]) / self.kernel_size[1] + 1)

        return H, W

    def forward(self, x):
        x = self.conv1(x)
        x = self.act_fn(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.act_fn(x)
        x = self.pool2(x)

        return x


@MODELS.register()
class CNNRULPredictor(NNModel):
    def __init__(self,
                 in_channels: int,
                 channels: int,
                 input_height: int,
                 input_width: int,
                 kernel_size=3,
                 act_fn: str = 'relu',
                 **kwargs):
        NNModel.__init__(self, **kwargs)
        self.channels = channels
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)
        if input_height < kernel_size[0]:
            kernel_size = (input_height, kernel_size[1])
        if input_width < kernel_size[1]:
            kernel_size = (kernel_size[0], input_width)
        self.encoder = ConvModule(in_channels, channels, kernel_size, act_fn)
        H, W = self.encoder.output_shape(input_height, input_width)
        self.proj = nn.Conv2d(channels, channels, (H, W))
        self.fc = nn.Linear(channels, 1)

    def forward(self,
                feature: torch.Tensor,
                label: torch.Tensor,
                return_loss: bool = False):
        if feature.ndim == 3:
            feature = feature.unsqueeze(1)
        x = self.encoder(feature)
        x = self.proj(x)
        x = x.view(-1, self.channels)
        x = torch.relu(x)
        x = self.fc(x).view(-1)

        if return_loss:
            if (x.abs().max() < 1e-5):
                return torch.inf
            return torch.mean((x - label.view(-1)) ** 2)  # L2 loss

        return x
