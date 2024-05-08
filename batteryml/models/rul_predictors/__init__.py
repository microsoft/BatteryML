# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from .cnn import CNNRULPredictor
from .mlp import MLPRULPredictor
from .pcr import PCRRULPredictor
from .svm import SVMRULPredictor
from .lstm import LSTMRULPredictor
from .plsr import PLSRRULPredictor
from .elastic_net import ElasticNetRULPredictor
from .random_forest import RandomForestRULPredictor
from .linear_regression import LinearRegressionRULPredictor
from .dummy import DummyRULPredictor
from .ridge import RidgeRULPredictor
from .gaussian_process import GaussianProcessRULPredictor
from .transformer import TransformerRULPredictor
from .xgb import XGBoostRULPredictor