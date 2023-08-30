# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, DotProduct

from src.builders import MODELS
from src.models.sklearn_model import SkleanModel


@MODELS.register()
class GaussianProcessRULPredictor(SkleanModel):
    def __init__(self, *args, workspace: str = None, **kwargs):
        SkleanModel.__init__(self, workspace)
        kernel = DotProduct() + RBF()
        self.model = GaussianProcessRegressor(kernel)
