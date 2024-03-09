# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from xgboost import XGBRegressor

from batteryml.builders import MODELS
from batteryml.models.sklearn_model import SklearnModel


@MODELS.register()
class XGBoostRULPredictor(SklearnModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SklearnModel.__init__(self, workspace)
        self.model = XGBRegressor(*args, **kwargs)
