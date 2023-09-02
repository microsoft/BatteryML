# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import math
import torch

from functools import partial

from batteryml.builders import DATA_TRANSFORMATIONS
from batteryml.data.transformation.base import BaseDataTransformation


def forward(base, x):
    return torch.log(x) / math.log(base)


@DATA_TRANSFORMATIONS.register()
class LogScaleDataTransformation(BaseDataTransformation):
    def __init__(self, base: float = None):
        self.base = base or math.e
        if base is None:
            self._func = torch.log
            self._inv_func = torch.exp
        else:
            self._func = partial(forward, base)
            self._inv_func = partial(torch.pow, base)

    @torch.no_grad()
    def transform(self, data: torch.Tensor) -> torch.Tensor:
        return self._func(data)

    @torch.no_grad()
    def inverse_transform(self, data: torch.Tensor) -> torch.Tensor:
        return self._inv_func(data)
