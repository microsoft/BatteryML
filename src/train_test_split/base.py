# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import abc

from pathlib import Path
from typing import List, Tuple


class BaseTrainTestSplitter(abc.ABC):
    def __init__(self, cell_data_path: List[str]):
        """Initialize a TrainTestSplitter object.

        Args:
            cell_data_path (list): path to files that records a battery's path
                                   per row or directories that contains the
                                   battery data.
        """
        if not isinstance(cell_data_path, list):
            cell_data_path = [cell_data_path]

        self._file_list = []
        for path in cell_data_path:
            path = Path(path)
            assert path.exists(), path

            if path.is_dir():
                self._file_list += list(path.glob('*.pkl'))
            else:
                with open(path, 'r') as fin:
                    self._file_list += fin.read().splitlines()

    @abc.abstractmethod
    def split(self) -> Tuple[List, List]:
        """Divide the dataset into train and test splits.

        Returns:
            Tuple[List, List]: train/test battery data lists.
        """
