# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from pathlib import Path

from batteryml.builders import TRAIN_TEST_SPLITTERS
from batteryml.train_test_split.base import BaseTrainTestSplitter

class MATRTrainTestSplitter(BaseTrainTestSplitter):
    def __init__(self, cell_data_path: str, train_ids: list, test_ids: list):
        BaseTrainTestSplitter.__init__(self, cell_data_path)
        # NOTE: the filename should be the cell IDs

        # Build a map from train_id to file_path
        path_map = {}
        for cell_path in self._file_list:
            cell_path = Path(cell_path)
            cell_id = cell_path.stem.split('_')[1]
            path_map[cell_id] = cell_path

        self.train_cells = [path_map[cell] for cell in train_ids]
        self.test_cells = [path_map[cell] for cell in test_ids]

        assert len(self.train_cells) == len(train_ids)
        assert len(self.test_cells) == len(test_ids)

    def split(self):
        return self.train_cells, self.test_cells


@TRAIN_TEST_SPLITTERS.register()
class MATRPrimaryTestTrainTestSplitter(MATRTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        train_ids = [
            'b1c1',  'b1c3',  'b1c5',  'b1c7',  'b1c11', 'b1c15',
            'b1c17', 'b1c19', 'b1c21', 'b1c24', 'b1c26', 'b1c28',
            'b1c30', 'b1c32', 'b1c34', 'b1c36', 'b1c38', 'b1c40',
            'b1c42', 'b1c44', 'b2c0',  'b2c2',  'b2c4',  'b2c6',
            'b2c11', 'b2c13', 'b2c17', 'b2c19', 'b2c21', 'b2c23',
            'b2c25', 'b2c27', 'b2c29', 'b2c31', 'b2c33', 'b2c35',
            'b2c37', 'b2c39', 'b2c41', 'b2c43', 'b2c45'
        ]
        test_ids = [
            'b1c0',  'b1c2',  'b1c4',  'b1c6',  'b1c9',  'b1c14',
            'b1c16', 'b1c18', 'b1c20', 'b1c23', 'b1c25', 'b1c27',
            'b1c29', 'b1c31', 'b1c33', 'b1c35', 'b1c37', 'b1c39',
            'b1c41', 'b1c43', 'b1c45', 'b2c1',  'b2c3',  'b2c5',
            'b2c10', 'b2c12', 'b2c14', 'b2c18', 'b2c20', 'b2c22',
            'b2c24', 'b2c26', 'b2c28', 'b2c30', 'b2c32', 'b2c34',
            'b2c36', 'b2c38', 'b2c40', 'b2c42', 'b2c44', 'b2c46',
            'b2c47']

        # NOTE: the Nature Energy and ECS papers do not deal with the
        #       outlier point b2c1. Actually, directly fitting an NN
        #       leads to large error on this cell. However, contrastive
        #       learning will not suffer from this issue. For fair
        #       comparison, here we delete it from the test split.
        #       You can always try to add it back to see the effect.
        test_ids.pop(test_ids.index('b2c1'))

        MATRTrainTestSplitter.__init__(
            self, cell_data_path, train_ids, test_ids)


@TRAIN_TEST_SPLITTERS.register()
class MATRSecondaryTestTrainTestSplitter(MATRTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        train_ids = [
            'b1c1',  'b1c3',  'b1c5',  'b1c7',  'b1c11', 'b1c15',
            'b1c17', 'b1c19', 'b1c21', 'b1c24', 'b1c26', 'b1c28',
            'b1c30', 'b1c32', 'b1c34', 'b1c36', 'b1c38', 'b1c40',
            'b1c42', 'b1c44', 'b2c0',  'b2c2',  'b2c4',  'b2c6',
            'b2c11', 'b2c13', 'b2c17', 'b2c19', 'b2c21', 'b2c23',
            'b2c25', 'b2c27', 'b2c29', 'b2c31', 'b2c33', 'b2c35',
            'b2c37', 'b2c39', 'b2c41', 'b2c43', 'b2c45'
        ]
        test_ids = [
            'b3c0',  'b3c1',  'b3c3',  'b3c4',  'b3c5',  'b3c6',
            'b3c7',  'b3c8',  'b3c9',  'b3c10', 'b3c11', 'b3c12',
            'b3c13', 'b3c14', 'b3c15', 'b3c16', 'b3c17', 'b3c18',
            'b3c19', 'b3c20', 'b3c21', 'b3c22', 'b3c24', 'b3c25',
            'b3c26', 'b3c27', 'b3c28', 'b3c29', 'b3c30', 'b3c31',
            'b3c33', 'b3c34', 'b3c35', 'b3c36', 'b3c38', 'b3c39',
            'b3c40', 'b3c41', 'b3c44', 'b3c45']
        MATRTrainTestSplitter.__init__(
            self, cell_data_path, train_ids, test_ids)


@TRAIN_TEST_SPLITTERS.register()
class MATRCLOTestTrainTestSplitter(MATRTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        # train_ids = [
        #     'b1c1',  'b1c3',  'b1c5',  'b1c7',  'b1c11', 'b1c15',
        #     'b1c17', 'b1c19', 'b1c21', 'b1c24', 'b1c26', 'b1c28',
        #     'b1c30', 'b1c32', 'b1c34', 'b1c36', 'b1c38', 'b1c40',
        #     'b1c42', 'b1c44', 'b2c0',  'b2c2',  'b2c4',  'b2c6',
        #     'b2c11', 'b2c13', 'b2c17', 'b2c19', 'b2c21', 'b2c23',
        #     'b2c25', 'b2c27', 'b2c29', 'b2c31', 'b2c33', 'b2c35',
        #     'b2c37', 'b2c39', 'b2c41', 'b2c43', 'b2c45', 'b1c0',
        #     'b1c2',  'b1c4',  'b1c6',  'b1c9',  'b1c14', 'b1c16',
        #     'b1c18', 'b1c20', 'b1c23', 'b1c25', 'b1c27', 'b1c29',
        #     'b1c31', 'b1c33', 'b1c35', 'b1c37', 'b1c39', 'b1c41',
        #     'b1c43', 'b1c45', 'b2c1',  'b2c3',  'b2c5',  'b2c10',
        #     'b2c12', 'b2c14', 'b2c18', 'b2c20', 'b2c22', 'b2c24',
        #     'b2c26', 'b2c28', 'b2c30', 'b2c32', 'b2c34', 'b2c36',
        #     'b2c38', 'b2c40', 'b2c42', 'b2c44', 'b2c46', 'b2c47',
        #     'b3c0',  'b3c1',  'b3c3',  'b3c4',  'b3c5',  'b3c6',
        #     'b3c7',  'b3c8',  'b3c9',  'b3c10', 'b3c11', 'b3c12',
        #     'b3c13', 'b3c14', 'b3c15', 'b3c16', 'b3c17', 'b3c18',
        #     'b3c19', 'b3c20', 'b3c21', 'b3c22', 'b3c24', 'b3c25',
        #     'b3c26', 'b3c27', 'b3c28', 'b3c29', 'b3c30', 'b3c31',
        #     'b3c33', 'b3c34', 'b3c35', 'b3c36', 'b3c38', 'b3c39',
        #     'b3c40', 'b3c41', 'b3c44', 'b3c45'
        # ]
        # test_ids = [
        #     'b4c0',  'b4c1',  'b4c2',  'b4c3',  'b4c4',  'b4c5',
        #     'b4c6', 'b4c7',  'b4c8',  'b4c9',  'b4c10', 'b4c11',
        #     'b4c12', 'b4c13', 'b4c14', 'b4c15', 'b4c16', 'b4c17',
        #     'b4c18', 'b4c19', 'b4c20', 'b4c21', 'b4c22', 'b4c23',
        #     'b4c24', 'b4c25', 'b4c26', 'b4c27', 'b4c28', 'b4c29',
        #     'b4c30', 'b4c31', 'b4c32', 'b4c33', 'b4c34', 'b4c35',
        #     'b4c36', 'b4c37', 'b4c38', 'b4c39', 'b4c40', 'b4c41',
        #     'b4c42', 'b4c43', 'b4c44']
        train_ids = [
            'b4c43', 'b1c7', 'b3c9', 'b2c6', 'b2c21', 'b4c27',
            'b2c13', 'b1c27', 'b3c11', 'b4c39', 'b2c33', 'b4c2',
            'b4c9', 'b1c44', 'b3c7', 'b1c37', 'b3c34', 'b3c27',
            'b2c36', 'b1c34', 'b2c5', 'b2c47', 'b1c35', 'b1c29',
            'b1c38', 'b2c1', 'b4c31', 'b2c43', 'b3c13', 'b4c5',
            'b4c8', 'b4c36', 'b1c13', 'b4c23', 'b4c29', 'b3c44',
            'b3c2', 'b2c22', 'b2c42', 'b3c33', 'b1c4', 'b3c16',
            'b3c24', 'b1c10', 'b4c32', 'b1c8', 'b1c17', 'b1c14',
            'b4c12', 'b3c15', 'b1c28', 'b3c23', 'b3c0', 'b4c40',
            'b3c36', 'b2c30', 'b1c15', 'b1c24', 'b2c0', 'b1c1',
            'b4c25', 'b1c2', 'b2c18', 'b3c28', 'b3c35', 'b1c21',
            'b1c5', 'b4c20', 'b1c9', 'b2c26', 'b4c44', 'b3c18',
            'b2c17', 'b1c33', 'b3c14', 'b4c15', 'b4c35', 'b2c3',
            'b2c12', 'b3c26', 'b4c18', 'b4c17', 'b1c26', 'b3c6',
            'b3c19', 'b1c16', 'b2c23', 'b1c39', 'b4c30', 'b2c4',
            'b1c12', 'b3c12', 'b4c34', 'b4c11', 'b3c31', 'b1c36',
            'b2c35', 'b3c38', 'b2c11', 'b2c38', 'b3c4', 'b4c38',
            'b3c43', 'b2c37', 'b4c4', 'b4c42', 'b4c0', 'b1c32']
        test_ids = [
            'b3c41', 'b3c22', 'b1c6', 'b3c32', 'b4c19', 'b4c22',
            'b4c33', 'b2c32', 'b1c43', 'b1c20', 'b4c24', 'b2c28',
            'b3c3', 'b1c45', 'b4c7', 'b1c19', 'b2c20', 'b2c31',
            'b4c10', 'b1c41', 'b2c24', 'b2c2', 'b2c10', 'b1c23',
            'b2c44', 'b2c25', 'b2c46', 'b3c42', 'b3c20', 'b1c3',
            'b1c11', 'b4c13', 'b1c22', 'b4c6', 'b3c8', 'b3c30',
            'b4c41', 'b4c14', 'b2c14', 'b2c41', 'b3c29', 'b3c1',
            'b4c28', 'b4c16', 'b2c45', 'b1c25', 'b1c31', 'b2c40',
            'b1c42', 'b4c26', 'b4c1', 'b2c27', 'b4c3', 'b1c30',
            'b4c37', 'b2c34', 'b1c40', 'b3c45', 'b2c19', 'b4c21',
            'b3c10', 'b3c39', 'b2c39', 'b3c21', 'b3c40', 'b3c5',
            'b2c29', 'b1c18', 'b3c25', 'b3c17']
        MATRTrainTestSplitter.__init__(
            self, cell_data_path, train_ids, test_ids)
