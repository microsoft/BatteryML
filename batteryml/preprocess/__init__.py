import logging
from .download import DOWNLOAD_LINKS, download_file
from .preprocess_CALCE import CALCEPreprocessor
from .preprocess_HNEI import HNEIPreprocessor
from .preprocess_HUST import HUSTPreprocessor
from .preprocess_MATR import MATRPreprocessor
from .preprocess_OX import OXPreprocessor
from .preprocess_RWTH import RWTHPreprocessor
from .preprocess_SNL import SNLPreprocessor
from .preprocess_UL_PUR import UL_PURPreprocessor
from .preprocess_arbin import ARBINPreprocessor
from .preprocess_neware import NEWAREPreprocessor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

SUPPORTED_SOURCES = {
    'DATASETS': ['CALCE', 'HNEI', 'HUST', 'MATR', 'OX', 'RWTH', 'SNL', 'UL_PUR'],
    'CYCLERS': ['ARBIN', 'BATTERYARCHIVE', "BIOLOGIC",  'INDIGO',  "LANDT", "MACCOR", 'NEWARE', 'NOVONIX']
}
