from typing import List, Tuple


from batteryml.builders import TRAIN_TEST_SPLITTERS
from batteryml.train_test_split.base import BaseTrainTestSplitter


@TRAIN_TEST_SPLITTERS.register()
class SNLTrainTestSplitter(BaseTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        BaseTrainTestSplitter.__init__(self, cell_data_path)
        test_ids = [
            'SNL_18650_LFP_25C_0-100_0.5-1C_a',
            'SNL_18650_LFP_25C_0-100_0.5-2C_a',
            'SNL_18650_LFP_25C_0-100_0.5-3C_a',
            'SNL_18650_LFP_25C_0-100_0.5-3C_b',
            'SNL_18650_LFP_35C_0-100_0.5-1C_b',
            'SNL_18650_LFP_35C_0-100_0.5-2C_a',
            'SNL_18650_NCA_15C_0-100_0.5-1C_a',
            'SNL_18650_NCA_15C_0-100_0.5-1C_b',
            'SNL_18650_NCA_25C_0-100_0.5-0.5C_a',
            'SNL_18650_NCA_25C_0-100_0.5-1C_a',
            'SNL_18650_NCA_25C_0-100_0.5-1C_b',
            'SNL_18650_NCA_25C_0-100_0.5-1C_c',
            'SNL_18650_NCA_25C_20-80_0.5-0.5C_a',
            'SNL_18650_NCA_25C_20-80_0.5-0.5C_b',
            'SNL_18650_NCA_25C_20-80_0.5-0.5C_c',
            'SNL_18650_NCA_35C_0-100_0.5-1C_a',
            'SNL_18650_NCA_35C_0-100_0.5-1C_d',
            'SNL_18650_NCA_35C_0-100_0.5-2C_b',
            'SNL_18650_NMC_15C_0-100_0.5-2C_b',
            'SNL_18650_NMC_25C_0-100_0.5-1C_d',
            'SNL_18650_NMC_25C_0-100_0.5-2C_b',
            'SNL_18650_NMC_25C_0-100_0.5-3C_c',
            'SNL_18650_NMC_25C_0-100_0.5-3C_d',
            'SNL_18650_NMC_35C_0-100_0.5-1C_b',
            'SNL_18650_NMC_35C_0-100_0.5-2C_b'
        ]


        self.train_cells, self.test_cells = [], []
        for filename in self._file_list:
            # filename like: HUST_1-1
            if filename.stem in test_ids:
                self.test_cells.append(filename)
            else:
                self.train_cells.append(filename)
    def split(self) -> Tuple[List, List]:
        return self.train_cells, self.test_cells
