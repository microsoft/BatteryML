from typing import List, Tuple


from batteryml.builders import TRAIN_TEST_SPLITTERS
from batteryml.train_test_split.base import BaseTrainTestSplitter


@TRAIN_TEST_SPLITTERS.register()
class CRUSHTrainTestSplitter(BaseTrainTestSplitter):
    def __init__(self, cell_data_path: str):
        BaseTrainTestSplitter.__init__(self, cell_data_path)
        test_ids = [
            'SNL_18650_NMC_35C_0-100_0.5-1C_c',
            'UL-PUR_N15-OV3_18650_NCA_23C_0-100_0.5-0.5C_c',
            'CALCE_CX2_34',
            'RWTH_016',
            'RWTH_006',
            'SNL_18650_NMC_25C_0-100_0.5-1C_a',
            'RWTH_038',
            'SNL_18650_NCA_35C_0-100_0.5-2C_a',
            'CALCE_CS2_33',
            'SNL_18650_LFP_25C_0-100_0.5-1C_d',
            'SNL_18650_LFP_25C_0-100_0.5-3C_c',
            'SNL_18650_LFP_35C_0-100_0.5-1C_d',
            'RWTH_026',
            'SNL_18650_LFP_35C_0-100_0.5-2C_b',
            'CALCE_CX2_37',
            'CALCE_CS2_34',
            'SNL_18650_NCA_35C_0-100_0.5-1C_b',
            'UL-PUR_N15-EX4_18650_NCA_23C_0-100_0.5-0.5C_d',
            'CALCE_CX2_33',
            'RWTH_008',
            'UL-PUR_N20-EX2_18650_NCA_23C_0-100_0.5-0.5C_b',
            'RWTH_031',
            'RWTH_036',
            'RWTH_045',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_t',
            'SNL_18650_LFP_25C_0-100_0.5-2C_a',
            'SNL_18650_LFP_25C_0-100_0.5-1C_b',
            'RWTH_015',
            'SNL_18650_NMC_35C_0-100_0.5-2C_b',
            'RWTH_020',
            'SNL_18650_NMC_25C_0-100_0.5-3C_a',
            'RWTH_046',
            'RWTH_035',
            'RWTH_017',
            'SNL_18650_LFP_35C_0-100_0.5-1C_a',
            'SNL_18650_NCA_25C_20-80_0.5-0.5C_d',
            'SNL_18650_NMC_15C_0-100_0.5-1C_a',
            'CALCE_CX2_35',
            'SNL_18650_NCA_15C_0-100_0.5-1C_a',
            'CALCE_CX2_38',
            'SNL_18650_LFP_25C_0-100_0.5-1C_c',
            'RWTH_012',
            'RWTH_039',
            'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_p',
            'SNL_18650_NMC_35C_0-100_0.5-1C_d',
            'RWTH_047',
            'RWTH_010',
            'SNL_18650_NMC_25C_0-100_0.5-3C_d',
            'RWTH_030',
            'SNL_18650_LFP_35C_0-100_0.5-2C_a',
            'SNL_18650_NMC_25C_0-100_0.5-1C_c',
            'SNL_18650_LFP_25C_0-100_0.5-1C_a',
            'SNL_18650_NCA_25C_0-100_0.5-2C_a',
            'SNL_18650_NMC_25C_0-100_0.5-2C_a',
            'SNL_18650_NMC_35C_0-100_0.5-1C_a',
            'RWTH_041',
            'CALCE_CX2_36',
            'SNL_18650_NCA_25C_20-80_0.5-0.5C_c',
            'SNL_18650_NCA_25C_0-100_0.5-0.5C_b'
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
