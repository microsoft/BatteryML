# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import abc
import torch
import shutil

from batteryml.data.databundle import DataBundle


class BaseModel(abc.ABC):
    """Scikit-learn-like interface for models."""
    def __init__(self, workspace: str = None):
        self.workspace = workspace

    @abc.abstractmethod
    def fit(self, dataset: DataBundle, timestamp: str = None):
        """Fit the dataset in an in-place manner.

        Args:
            dataset (DataBundle): dataset for training.
            timestamp (str): current timestamp for saving checkpoints.
        """

    @abc.abstractmethod
    def predict(self, dataset: DataBundle, data_type: str='test') -> torch.Tensor:
        """Predict the degradation labels."""

    @abc.abstractmethod
    def dump_checkpoint(self, path: str):
        """Dump checkpoint to disk."""

    @abc.abstractmethod
    def load_checkpoint(self, path: str):
        """Load checkpoint from disk."""

    def to(self, device: str):
        """Move the model to the device."""
        return self

    def link_latest_checkpoint(self, filename: str):
        to_dump = self.workspace / 'latest.ckpt'
        shutil.copyfile(filename, to_dump)
