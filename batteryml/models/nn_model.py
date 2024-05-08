# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import abc
import torch
import random
import numpy as np
import torch.nn as nn
import torch.optim as optim

from tqdm import tqdm
from torch.utils.data.dataloader import DataLoader

from batteryml.data import DataBundle

from .base import BaseModel


def seed_worker(worker_id):
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


class NNModel(BaseModel, nn.Module, abc.ABC):
    def __init__(self,
                 batch_size: int = 32,
                 epochs: int = 10000,
                 workspace: str = None,
                 evaluate_freq: int = 500,
                 checkpoint_freq: int = 1000,
                 train_batch_size: int = None,
                 test_batch_size: int = None,
                 lr: float = 1e-3):
        nn.Module.__init__(self)
        BaseModel.__init__(self, workspace)
        self.train_epochs = epochs
        self.evaluate_freq = evaluate_freq
        if checkpoint_freq is None or checkpoint_freq == 'None':
            self.checkpoint_freq = None
        else:
            self.checkpoint_freq = min(checkpoint_freq, self.train_epochs)
        self.train_batch_size = train_batch_size or batch_size
        self.test_batch_size = test_batch_size or batch_size
        self.lr = lr

    def fit(self,
            dataset: DataBundle,
            timestamp: str = None,
            seed: int = 0):
        self.train()
        train_data = dataset.train_data
        loader = DataLoader(
            train_data, self.train_batch_size,
            shuffle=True, worker_init_fn=seed_worker)
        # TODO: support customization of optimizers
        optimizer = optim.Adam(self.parameters(), lr=self.lr)

        timestamp = timestamp or 'UnknownTime'

        latest = None
        for epoch in tqdm(range(self.train_epochs), desc='Traning'):
            self.train()
            for batch in loader:
                loss = self.forward(**batch, return_loss=True)
                if loss == torch.inf:
                    reset_parameters(self)
                    optimizer = optim.Adam(self.parameters(), lr=self.lr)
                else:
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

            if self.checkpoint_freq is not None and \
                    (epoch + 1) % self.checkpoint_freq == 0:
                filename = f'{timestamp}_seed_{seed}_epoch_{epoch+1}.ckpt'
                if self.workspace is not None:
                    self.dump_checkpoint(self.workspace / filename)
                    latest = self.workspace / filename

            if (epoch + 1) % self.evaluate_freq == 0:
                pred = self.predict(dataset)
                score = dataset.evaluate(pred, 'RMSE')
                print(f'[{epoch+1}/{self.train_epochs}] RMSE {score:.2f}', flush=True)

        if self.workspace is not None:
            self.link_latest_checkpoint(latest)

    @torch.no_grad()
    def predict(self, dataset: DataBundle, data_type: str='test') -> torch.Tensor:
        self.eval()
        # test_data = dataset.test_data
        if data_type == 'test':
            test_data = dataset.test_data
        else:
            test_data = dataset.train_data
            
        loader = DataLoader(
            test_data, self.test_batch_size,
            shuffle=False, worker_init_fn=seed_worker)
        predictions = torch.cat([self.forward(**batch) for batch in loader])
        return predictions

    def to(self, device: str):
        return nn.Module.to(self, device)

    def dump_checkpoint(self, path: str):
        torch.save(self.state_dict(), path)

    def load_checkpoint(self, path: str):
        self.load_state_dict(torch.load(path))


def reset_parameters(model):
    @torch.no_grad()
    def weight_reset(m):
        reset_parameters = getattr(m, "reset_parameters", None)
        if callable(reset_parameters):
            m.reset_parameters()

    model.apply(weight_reset)
