# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import os
import importlib

from tqdm import tqdm
from pathlib import Path


def import_function(path: Path or str) -> callable:
    # convert the path to a string if it is a pathlib.Path object
    if isinstance(path, Path):
        path = str(path)
    # get the file name without the extension
    filename = Path(path).stem
    # create a module specification from the file path
    spec = importlib.util.spec_from_file_location(filename, path)
    # create a module object from the specification
    module = importlib.util.module_from_spec(spec)
    # execute the module code
    spec.loader.exec_module(module)
    # get the function object from the module
    function = module.__dict__.get('preprocess')
    # return the function object
    return function


if __name__ == '__main__':
    script_path = Path(__file__).parent / 'preprocess_scripts'
    raw_data_path = Path(__file__).parent.parent / 'data/raw'
    processed_data_path = Path(__file__).parent.parent / 'data/processed'

    pbar = tqdm([
        raw_data_path / 'SNL',
        raw_data_path / 'OX',
        raw_data_path / 'UL_PUR',
        raw_data_path / 'HNEI',
        raw_data_path / 'MATR',
        raw_data_path / 'HUST',
        raw_data_path / 'RWTH',
        raw_data_path / 'CALCE',
    ])

    for path in pbar:
        dataset = path.stem
        store_dir = processed_data_path / dataset

        if not store_dir.exists():
            os.makedirs(store_dir)

        # Already processed
        if len(list(store_dir.glob('*.pkl'))) > 0:
            continue

        pbar.set_description(f'Processing dataset {dataset}')

        preprocess = import_function(script_path / f'preprocess_{dataset}.py')
        cells = preprocess(path)

        if cells is None:
            continue

        # Dump to disk, one file per cell
        for cell in tqdm(cells, desc='Save the cells to disk', leave=False):
            store_path = store_dir / f'{cell.cell_id}.pkl'
            cell.dump(store_path)
