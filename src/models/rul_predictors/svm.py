# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from sklearn.svm import SVR

from src.builders import MODELS
from src.models.sklearn_model import SklearnModel


@MODELS.register()
class SVMRULPredictor(SklearnModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SklearnModel.__init__(self, workspace)
        self.model = SVR(*args, **kwargs)
