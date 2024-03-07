# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from typing import List, Tuple


from batteryml.builders import TRAIN_TEST_SPLITTERS
from batteryml.train_test_split.base import BaseTrainTestSplitter


@TRAIN_TEST_SPLITTERS.register()
class HUSTTrainTestSplitter(BaseTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        BaseTrainTestSplitter.__init__(self, cell_data_path)

        train_ids = [
            '1-3',  '1-4',  '1-5',  '1-6',  '1-7',  '1-8',  '2-2',  '2-3',
            '2-4',  '2-6',  '2-7',  '2-8',  '3-2',  '3-3',  '3-4',  '3-5',
            '3-6',  '3-7',  '3-8',  '4-1',  '4-2',  '4-3',  '4-4',  '4-6',
            '4-7',  '4-8',  '5-1',  '5-2',  '5-4',  '5-5',  '5-6',  '5-7',
            '6-3',  '6-4',  '6-5',  '7-1',  '7-2',  '7-3',  '7-4',  '7-7',
            '7-8',  '8-2',  '8-3',  '8-4',  '8-7',  '9-1',  '9-2',  '9-3',
            '9-5',  '9-7',  '9-8',  '10-2', '10-3', '10-5', '10-8']
        # valid_ids = ['4-3', '5-7', '3-3', '2-3', '9-3', '10-5', '3-2', '3-7']
        # train_ids = [
        #     '9-1', '2-2', '4-7','9-7', '1-8','4-6','2-7','8-4', '7-2',
        #     '10-3', '2-4', '7-4', '3-4', '5-4', '8-7','7-7', '4-4', '1-3',
        #     '7-1','5-2', '6-4', '9-8','9-5','6-3','10-8','1-6', '3-5',
        #     '2-6', '3-8', '3-6', '4-8', '7-8','5-1', '2-8', '8-2', '1-5',
        #     '7-3', '10-2','5-5', '9-2','5-6', '1-7', '8-3', '4-1', '4-2',
        #     '1-4','6-5']
        # test_ids = [
        #     '1-1',  '1-2',  '2-5',  '3-1',  '4-5',  '5-3',  '6-1',  '6-2',
        #     '6-6',  '6-8',  '7-5',  '7-6',  '8-1',  '8-5',  '8-6',  '8-8',
        #     '9-4',  '9-6',  '10-1', '10-4', '10-6', '10-7']

        self.train_cells, self.test_cells = [], []

        for filename in self._file_list:
            # filename like: HUST_1-1.pkl
            if filename.stem.split('_')[1] in train_ids:
                self.train_cells.append(filename)
            else:
                self.test_cells.append(filename)

    def split(self) -> Tuple[List, List]:
        return self.train_cells, self.test_cells
