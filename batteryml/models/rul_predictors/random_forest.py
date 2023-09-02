# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from sklearn.ensemble import RandomForestRegressor

from batteryml.builders import MODELS
from batteryml.models.sklearn_model import SkleanModel


@MODELS.register()
class RandomForestRULPredictor(SkleanModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SkleanModel.__init__(self, workspace)
        self.model = RandomForestRegressor(*args, **kwargs)
