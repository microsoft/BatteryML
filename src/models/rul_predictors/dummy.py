# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from sklearn.dummy import DummyRegressor

from src.builders import MODELS
from src.models.sklearn_model import SkleanModel


@MODELS.register()
class DummyRULPredictor(SkleanModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SkleanModel.__init__(self, workspace)
        self.model = DummyRegressor(**kwargs)
