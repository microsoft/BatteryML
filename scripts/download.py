# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import os
import time
import math
import requests

from tqdm import tqdm
from pathlib import Path


def download_file(url,
                  filename,
                  update_interval=500,
                  chunk_size=4096,
                  total_length=None,
                  force=False):
    def memory2str(mem):
        sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        power = int(math.log(mem, 1024))
        size = sizes[power]
        for _ in range(power):
            mem /= 1024
        if power > 0:
            return f'{mem:.2f}{size}'
        else:
            return f'{mem}{size}'
    if not filename.parent.exists():
        filename.parent.mkdir()
    if filename.exists() and not force:
        print(f'[INFO] {filename} already exists. Skip it.')
        return
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        if total_length is None:
            total_length = response.headers.get('content-length')
        if response.status_code != 200:
            raise ValueError(
                f'Network error: {response.status_code}! URL: {url}')
        if total_length is None:
            f.write(response.content)
        else:
            print(f'[INFO] Downloads saving to {filename}.', flush=True)
            downloaded, total_length = 0, int(total_length)
            total_size = memory2str(total_length)
            bar_format = (
                '{percentage:3.0f}%|{bar:20}| {desc} '
                '[{elapsed}<{remaining}{postfix}]')
            if update_interval * chunk_size * 100 >= total_length:
                update_interval = 1
            with tqdm(total=total_length, bar_format=bar_format) as bar:
                counter = 0
                now_time, now_size = time.time(), downloaded
                for data in response.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    downloaded += len(data)
                    counter += 1
                    bar.update(len(data))
                    if counter % update_interval == 0:
                        ellapsed = time.time() - now_time
                        runtime_downloaded = downloaded - now_size
                        now_time, now_size = time.time(), downloaded

                        cur_size = memory2str(downloaded)
                        speed_size = memory2str(runtime_downloaded / ellapsed)
                        bar.set_description(f'{cur_size}/{total_size}')
                        bar.set_postfix_str(f'{speed_size}/s')

                        counter = 0


# The list of raw data files to be downloaded
MATR_LINKS = (
    ('https://data.matr.io/1/api/v1/file/5c86c0b5fa2ede00015ddf66/download',
     '2017-05-12_batchdata_updated_struct_errorcorrect.mat'),
    ('https://data.matr.io/1/api/v1/file/5c86bf13fa2ede00015ddd82/download',
     '2017-06-30_batchdata_updated_struct_errorcorrect.mat'),
    ('https://data.matr.io/1/api/v1/file/5c86bd64fa2ede00015ddbb2/download',
     '2018-04-12_batchdata_updated_struct_errorcorrect.mat'),
    ('https://data.matr.io/1/api/v1/file/5dcef152110002c7215b2c90/download',
     '2019-01-24_batchdata_updated_struct_errorcorrect.mat')
)

HUST_LINKS = (
    ('https://data.mendeley.com/public-files/datasets/nsc7hnsg4s/'
     'files/5ca0ac3e-d598-4d07-8dcb-879aa047e98b/file_downloaded',
     'hust_data.zip'),
)

CALCE_LINKS = (
    ('https://web.calce.umd.edu/batteries/data/CS2_33.zip', 'CS2_33.zip'),
    ('https://web.calce.umd.edu/batteries/data/CS2_34.zip', 'CS2_34.zip'),
    ('https://web.calce.umd.edu/batteries/data/CS2_35.zip', 'CS2_35.zip'),
    ('https://web.calce.umd.edu/batteries/data/CS2_36.zip', 'CS2_36.zip'),
    ('https://web.calce.umd.edu/batteries/data/CS2_37.zip', 'CS2_37.zip'),
    ('https://web.calce.umd.edu/batteries/data/CS2_38.zip', 'CS2_38.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_16.zip', 'CX2_16.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_33.zip', 'CX2_33.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_35.zip', 'CX2_35.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_34.zip', 'CX2_34.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_36.zip', 'CX2_36.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_37.zip', 'CX2_37.zip'),
    ('https://web.calce.umd.edu/batteries/data/CX2_38.zip', 'CX2_38.zip'),
)


RWTH_LINKS = (
    ('https://publications.rwth-aachen.de/record/818642/files/Rawdata.zip',
     'raw.zip'),
)


def get_links():
    return {
        # NOTE: batteryarchive.com stops their download service. For OX, SNL,
        #       HNEI, UL_PUR datasets, please contact them for access.
        'HUST': HUST_LINKS,
        'MATR': MATR_LINKS,
        'CALCE': CALCE_LINKS,
        'RWTH': RWTH_LINKS
    }


def download_raw_data(dataset_name=None):
    """
    Download battery public datasets.

    Parameters:
        dataset_name (str, optional): The name of the specific dataset to download.
            If set to None (default), all preset datasets will be downloaded.
            Available preset datasets: HUST, MATR, CALCE, RWTH, KIT_FOBOSS.
            Note: batteryarchive.com has stopped their download service.
            For OX, SNL, HNEI, and UL_PUR datasets, please contact the respective organizations for access.
    """

    home = Path(__file__).parent.parent / 'data'
    raw_dir = home / 'raw'
    if not raw_dir.exists():
        raw_dir.mkdir()
    all_links = get_links()
    selected_links = {}
    if isinstance(dataset_name, str) and dataset_name:
        selected_links[dataset_name.upper()] = all_links[dataset_name.upper()]
    else:
        selected_links = all_links

    for dataset, files in selected_links.items():
        path = raw_dir / dataset
        for f in files:
            if len(f) == 2:
                (url, filename), total_length = f, None
            else:
                url, filename, total_length = f
            download_file(url, path / filename, total_length=total_length)

    print(f'[INFO] {list(selected_links.keys())} datasets downloaded.')

if __name__ == '__main__':
    download_raw_data(dataset_name=None)