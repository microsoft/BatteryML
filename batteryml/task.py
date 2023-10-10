# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch

from tqdm import tqdm

from batteryml.builders import (
    FEATURE_EXTRACTORS,
    LABEL_ANNOTATORS,
    TRAIN_TEST_SPLITTERS,
    DATA_TRANSFORMATIONS
)
from batteryml.data import BatteryData, DataBundle
from batteryml.data.transformation.base import BaseDataTransformation


class Task:
    def __init__(self,
                 train_test_splitter: dict,
                 feature_extractor: dict,
                 label_annotator: dict,
                 feature_transformation: BaseDataTransformation = None,
                 label_transformation: BaseDataTransformation = None):
        if isinstance(train_test_splitter, dict):
            train_test_splitter = \
                TRAIN_TEST_SPLITTERS.build(train_test_splitter, 'raise')
        if isinstance(feature_extractor, dict):
            feature_extractor = FEATURE_EXTRACTORS.build(feature_extractor)
        if isinstance(label_annotator, dict):
            label_annotator = LABEL_ANNOTATORS.build(label_annotator)
        if isinstance(feature_transformation, dict):
            feature_transformation = DATA_TRANSFORMATIONS.build(
                feature_transformation)
        if isinstance(label_transformation, dict):
            label_transformation = DATA_TRANSFORMATIONS.build(
                label_transformation)

        self.train_test_splitter = train_test_splitter
        self.feature_extractor = feature_extractor
        self.label_annotator = label_annotator
        self.feature_transformation = feature_transformation
        self.label_transformation = label_transformation

    def build(self) -> DataBundle:
        # Loading data
        train_list, test_list = self.train_test_splitter.split()
        pbar = tqdm(train_list, desc='Reading train data')
        train_cells = [BatteryData.load(path) for path in pbar]
        pbar = tqdm(test_list, desc='Reading test data')
        test_cells = [BatteryData.load(path) for path in pbar]

        self.train_cells = train_cells
        self.test_cells = test_cells

        # Extracting features
        train_features = self.feature_extractor(train_cells)
        test_features = self.feature_extractor(test_cells)
        train_labels = self.label_annotator(train_cells)
        test_labels = self.label_annotator(test_cells)

        # Omit NaN label cells
        train_mask = ~torch.isnan(train_labels)
        test_mask = ~torch.isnan(test_labels)
        train_features = train_features[train_mask]
        test_features = test_features[test_mask]
        train_labels = train_labels[train_mask]
        test_labels = test_labels[test_mask]

        dataset = DataBundle(
            train_features, train_labels, test_features, test_labels,
            feature_transformation=self.feature_transformation,
            label_transformation=self.label_transformation
        )

        return dataset

    def get_raw_data(self):
        return self.train_cells, self.test_cells
