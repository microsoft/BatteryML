# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import abc
import torch


class BaseDataTransformation(abc.ABC):
    def fit(self, data: torch.Tensor) -> torch.Tensor:
        """Fit the parameters for stateful transformations."""

    def transform(self, data: torch.Tensor) -> torch.Tensor:
        """Transform a data tensor and return a same-sized tensor."""

    def inverse_transform(self, data: torch.Tensor) -> torch.Tensor:
        """Inverse-transform a data tensor and return a same-sized tensor."""

    def to(self, device):
        """Map the transformation object to specific group."""
        return self
