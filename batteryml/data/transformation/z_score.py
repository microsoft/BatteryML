# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from batteryml.builders import DATA_TRANSFORMATIONS
from batteryml.data.transformation.base import BaseDataTransformation


@DATA_TRANSFORMATIONS.register()
class ZScoreDataTransformation(BaseDataTransformation):
    def __init__(self):
        self._mean = None
        self._std = None

    def fit(self, data: torch.Tensor) -> torch.Tensor:
        self._mean = data.mean(0, keepdim=True)
        self._std = torch.clamp(data.std(0, keepdim=True), min=1e-8)

    def assert_fitted(self):
        assert self._mean is not None, 'Transformation not fitted!'
        assert self._std is not None, 'Transformation not fitted!'

    @torch.no_grad()
    def transform(self, data: torch.Tensor) -> torch.Tensor:
        self.assert_fitted()
        data = (data - self._mean) / self._std
        return data

    @torch.no_grad()
    def inverse_transform(self, data: torch.Tensor) -> torch.Tensor:
        self.assert_fitted()
        data = data * self._std + self._mean
        return data

    def to(self, device):
        self._mean = self._mean.to(device)
        self._std = self._std.to(device)
        return self
