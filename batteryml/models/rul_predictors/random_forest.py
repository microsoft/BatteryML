# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from sklearn.ensemble import RandomForestRegressor

from batteryml.builders import MODELS
from batteryml.models.sklearn_model import SklearnModel


@MODELS.register()
class RandomForestRULPredictor(SklearnModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SklearnModel.__init__(self, workspace)
        self.model = RandomForestRegressor(*args, **kwargs)
