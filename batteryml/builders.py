# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from batteryml.utils.registry import Registry

MODELS = Registry('Models')
PREPROCESSORS = Registry('Preprocessors')
LABEL_ANNOTATORS = Registry('Label Annotators')
FEATURE_EXTRACTORS = Registry('Feature Extractors')
TRAIN_TEST_SPLITTERS = Registry('Train Test Splitters')
DATA_TRANSFORMATIONS = Registry('Data Transformations')
