# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from typing import List

import torch

from batteryml.builders import DATA_TRANSFORMATIONS
from batteryml.data.transformation.base import BaseDataTransformation


@DATA_TRANSFORMATIONS.register()
class SequentialDataTransformation(BaseDataTransformation):
    def __init__(self, transformations: List[BaseDataTransformation]):
        self.transformations = []
        for trans in transformations:
            if isinstance(trans, dict):
                trans = DATA_TRANSFORMATIONS.build(trans)
            self.transformations.append(trans)

    @torch.no_grad()
    def fit(self, data: torch.Tensor) -> torch.Tensor:
        for trans in self.transformations:
            trans.fit(data)
            data = trans.transform(data)

    @torch.no_grad()
    def transform(self, data: torch.Tensor) -> torch.Tensor:
        for trans in self.transformations:
            data = trans.transform(data)
        return data

    @torch.no_grad()
    def inverse_transform(self, data: torch.Tensor) -> torch.Tensor:
        for trans in self.transformations[::-1]:
            data = trans.inverse_transform(data)
        return data

    def to(self, device):
        self.transformations = [t.to(device) for t in self.transformations]
        return self
