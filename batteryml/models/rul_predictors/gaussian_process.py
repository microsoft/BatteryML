# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, DotProduct

from batteryml.builders import MODELS
from batteryml.models.sklearn_model import SklearnModel


@MODELS.register()
class GaussianProcessRULPredictor(SklearnModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SklearnModel.__init__(self, workspace)
        kernel = DotProduct() + RBF()
        self.model = GaussianProcessRegressor(kernel)
