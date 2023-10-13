from .download import Downloader, DOWNLOAD_LINKS
from .preprocess_CALCE import CALCEPreprocessor
from .preprocess_HNEI import HNEIPreprocessor
from .preprocess_HUST import HUSTPreprocessor
from .preprocess_MATR import MATRPreprocessor
from .preprocess_OX import OXPreprocessor
from .preprocess_RWTH import RWTHPreprocessor
from .preprocess_SNL import SNLPreprocessor
from .preprocess_UL_PUR import ULPURPreprocessor


SUPPORTED_SOURCES = [
    'CALCE', 'HNEI', 'HUST', 'MATR', 'OX', 'RWTH', 'SNL', 'UL_PUR'
]