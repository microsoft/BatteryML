from typing import List, Tuple


from batteryml.builders import TRAIN_TEST_SPLITTERS
from batteryml.train_test_split.base import BaseTrainTestSplitter


@TRAIN_TEST_SPLITTERS.register()
class CRUHTrainTestSplitter(BaseTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        BaseTrainTestSplitter.__init__(self, cell_data_path)

        test_ids = [
            'RWTH_015',
            'UL-PUR_N15-OV3_18650_NCA_23C_0-100_0.5-0.5C_c',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_j',
            'RWTH_048',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_n',
            'CALCE_CX2_16',
            'RWTH_010',
            'RWTH_005',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_l',
            'RWTH_018',
            'RWTH_029',
            'RWTH_032',
            'CALCE_CX2_35',
            'RWTH_043',
            'RWTH_014',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_f',
            'RWTH_007',
            'CALCE_CX2_38',
            'RWTH_046',
            'RWTH_011',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_e',
            'RWTH_039',
            'RWTH_002',
            'RWTH_049',
            'RWTH_020',
            'RWTH_036',
            'RWTH_013',
            'RWTH_026',
            'RWTH_037',
            'RWTH_040',
            'RWTH_008',
            'CALCE_CS2_38',
            'RWTH_028',
            'RWTH_024'
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
