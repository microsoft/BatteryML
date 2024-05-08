# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import random

from batteryml.builders import TRAIN_TEST_SPLITTERS

from batteryml.train_test_split.base import BaseTrainTestSplitter


@TRAIN_TEST_SPLITTERS.register()
class RandomTrainTestSplitter(BaseTrainTestSplitter):
    def __init__(self,
                 cell_data_path: str,
                 seed: int = 0,
                 cell_to_drop: list = None,
                 *,
                 train_test_split_ratio: float = 0.6):
        BaseTrainTestSplitter.__init__(self, cell_data_path)
        self.seed = seed
        self.p = train_test_split_ratio

        if cell_to_drop is None:
            cell_to_drop = []
        if isinstance(cell_to_drop, int):
            cell_to_drop = [cell_to_drop]
        self.cell_to_drop = cell_to_drop

    def split(self):
        def _filter_cells(names):
            result = []
            for name in names:
                basename = name.rsplit('/', 1)[1]
                for cell in self.cell_to_drop:
                    if cell in basename:
                        continue
                result.append(name)
            return result
        random.seed(self.seed)
        shuffled = [str(x) for x in self._file_list]
        shuffled.sort()
        random.shuffle(shuffled)
        split_point = int(self.p * len(shuffled))
        train, test = shuffled[:split_point], shuffled[split_point:]
        # Drop cells if needed
        if self.cell_to_drop:
            train = _filter_cells(train)
            test = _filter_cells(test)
        return train, test
