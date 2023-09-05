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
# NOTE: Please download this file manually to data/raw/STANFORD
STANFORD_LINKS = (
    'https://files.osf.io/v1/resources/qsabn/providers/dropbox/?view_only=2a03b6c78ef14922a3e244f3d549de78&zip=')

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

KIT_FOBOSS_LINKS = (
    ('https://bwdatadiss.kit.edu/dataitem/download/3555', 'KIT_FOBOSS.zip'),
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

SNL_LINKS = (
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_LFP_15C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_LFP_15C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_LFP_15C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_LFP_15C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_LFP_15C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_LFP_15C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_LFP_15C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_15C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_LFP_15C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_c_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_c_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_d_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-1C_d_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-1C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_a_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_b_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_b_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_c_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_c_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_d_timeseries.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_0-100_0.5-3C_d_cycle_data.csv',
     'SNL_18650_LFP_25C_0-100_0.5-3C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_c_timeseries.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_c_cycle_data.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_d_timeseries.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-0.5C_d_cycle_data.csv',
     'SNL_18650_LFP_25C_20-80_0.5-0.5C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-3C_a_timeseries.csv',
     'SNL_18650_LFP_25C_20-80_0.5-3C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_20-80_0.5-3C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_20-80_0.5-3C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_LFP_25C_40-60_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_40-60_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_LFP_25C_40-60_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_LFP_25C_40-60_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-3C_a_timeseries.csv',
     'SNL_18650_LFP_25C_40-60_0.5-3C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-3C_a_cycle_data.csv',
     'SNL_18650_LFP_25C_40-60_0.5-3C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-3C_b_timeseries.csv',
     'SNL_18650_LFP_25C_40-60_0.5-3C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_25C_40-60_0.5-3C_b_cycle_data.csv',
     'SNL_18650_LFP_25C_40-60_0.5-3C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_c_timeseries.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_c_cycle_data.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_d_timeseries.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-1C_d_cycle_data.csv',
     'SNL_18650_LFP_35C_0-100_0.5-1C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_LFP_35C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_LFP_35C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_LFP_35C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_LFP_35C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_LFP_35C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_NCA_15C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_NCA_15C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_NCA_15C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_NCA_15C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_NCA_15C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_NCA_15C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_NCA_15C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_15C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_NCA_15C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_c_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_c_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_d_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-1C_d_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-1C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_NCA_25C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_NCA_25C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_c_timeseries.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_c_cycle_data.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_d_timeseries.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_20-80_0.5-0.5C_d_cycle_data.csv',
     'SNL_18650_NCA_25C_20-80_0.5-0.5C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_40-60_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_NCA_25C_40-60_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_40-60_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_NCA_25C_40-60_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_40-60_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_NCA_25C_40-60_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_25C_40-60_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_NCA_25C_40-60_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_c_timeseries.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_c_cycle_data.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_d_timeseries.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-1C_d_cycle_data.csv',
     'SNL_18650_NCA_35C_0-100_0.5-1C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_NCA_35C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_NCA_35C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_NCA_35C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NCA_35C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_NCA_35C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_NMC_15C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_NMC_15C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_NMC_15C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_NMC_15C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_NMC_15C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_NMC_15C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_NMC_15C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_15C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_NMC_15C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_c_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_c_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_d_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-1C_d_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-1C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-2C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-2C_b_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-2C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-2C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-2C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_a_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_b_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_c_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_c_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_d_timeseries.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_0-100_0.5-3C_d_cycle_data.csv',
     'SNL_18650_NMC_25C_0-100_0.5-3C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_c_timeseries.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_c_cycle_data.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_d_timeseries.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-0.5C_d_cycle_data.csv',
     'SNL_18650_NMC_25C_20-80_0.5-0.5C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-3C_a_timeseries.csv',
     'SNL_18650_NMC_25C_20-80_0.5-3C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-3C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_20-80_0.5-3C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-3C_b_timeseries.csv',
     'SNL_18650_NMC_25C_20-80_0.5-3C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_20-80_0.5-3C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_20-80_0.5-3C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-0.5C_a_timeseries.csv',
     'SNL_18650_NMC_25C_40-60_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-0.5C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_40-60_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-0.5C_b_timeseries.csv',
     'SNL_18650_NMC_25C_40-60_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-0.5C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_40-60_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-3C_a_timeseries.csv',
     'SNL_18650_NMC_25C_40-60_0.5-3C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-3C_a_cycle_data.csv',
     'SNL_18650_NMC_25C_40-60_0.5-3C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-3C_b_timeseries.csv',
     'SNL_18650_NMC_25C_40-60_0.5-3C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_25C_40-60_0.5-3C_b_cycle_data.csv',
     'SNL_18650_NMC_25C_40-60_0.5-3C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_a_timeseries.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_a_cycle_data.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_b_timeseries.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_b_cycle_data.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_c_timeseries.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_c_cycle_data.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_d_timeseries.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-1C_d_cycle_data.csv',
     'SNL_18650_NMC_35C_0-100_0.5-1C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-2C_a_timeseries.csv',
     'SNL_18650_NMC_35C_0-100_0.5-2C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/SNL_18650_NMC_35C_0-100_0.5-2C_a_cycle_data.csv',
     'SNL_18650_NMC_35C_0-100_0.5-2C_a_cycle_data.csv'),
)

UL_PUR_LINKS = (
    ('https://www.batteryarchive.org/data/UL-PUR_N10-EX9_18650_NCA_23C_0-100_0.5-0.5C_i_timeseries.csv',
     'UL-PUR_N10-EX9_18650_NCA_23C_0-100_0.5-0.5C_i_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N10-EX9_18650_NCA_23C_0-100_0.5-0.5C_i_cycle_data.csv',
     'UL-PUR_N10-EX9_18650_NCA_23C_0-100_0.5-0.5C_i_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N10-NA7_18650_NCA_23C_0-100_0.5-0.5C_g_timeseries.csv',
     'UL-PUR_N10-NA7_18650_NCA_23C_0-100_0.5-0.5C_g_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N10-NA7_18650_NCA_23C_0-100_0.5-0.5C_g_cycle_data.csv',
     'UL-PUR_N10-NA7_18650_NCA_23C_0-100_0.5-0.5C_g_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N10-OV8_18650_NCA_23C_0-100_0.5-0.5C_h_timeseries.csv',
     'UL-PUR_N10-OV8_18650_NCA_23C_0-100_0.5-0.5C_h_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N10-OV8_18650_NCA_23C_0-100_0.5-0.5C_h_cycle_data.csv',
     'UL-PUR_N10-OV8_18650_NCA_23C_0-100_0.5-0.5C_h_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N15-EX4_18650_NCA_23C_0-100_0.5-0.5C_d_timeseries.csv',
     'UL-PUR_N15-EX4_18650_NCA_23C_0-100_0.5-0.5C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N15-EX4_18650_NCA_23C_0-100_0.5-0.5C_d_cycle_data.csv',
     'UL-PUR_N15-EX4_18650_NCA_23C_0-100_0.5-0.5C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N15-NA10_18650_NCA_23C_0-100_0.5-0.5C_j_timeseries.csv',
     'UL-PUR_N15-NA10_18650_NCA_23C_0-100_0.5-0.5C_j_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N15-NA10_18650_NCA_23C_0-100_0.5-0.5C_j_cycle_data.csv',
     'UL-PUR_N15-NA10_18650_NCA_23C_0-100_0.5-0.5C_j_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N15-OV3_18650_NCA_23C_0-100_0.5-0.5C_c_timeseries.csv',
     'UL-PUR_N15-OV3_18650_NCA_23C_0-100_0.5-0.5C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N15-OV3_18650_NCA_23C_0-100_0.5-0.5C_c_cycle_data.csv',
     'UL-PUR_N15-OV3_18650_NCA_23C_0-100_0.5-0.5C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-EX2_18650_NCA_23C_0-100_0.5-0.5C_b_timeseries.csv',
     'UL-PUR_N20-EX2_18650_NCA_23C_0-100_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-EX2_18650_NCA_23C_0-100_0.5-0.5C_b_cycle_data.csv',
     'UL-PUR_N20-EX2_18650_NCA_23C_0-100_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-NA5_18650_NCA_23C_0-100_0.5-0.5C_e_timeseries.csv',
     'UL-PUR_N20-NA5_18650_NCA_23C_0-100_0.5-0.5C_e_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-NA5_18650_NCA_23C_0-100_0.5-0.5C_e_cycle_data.csv',
     'UL-PUR_N20-NA5_18650_NCA_23C_0-100_0.5-0.5C_e_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-NA6_18650_NCA_23C_0-100_0.5-0.5C_f_timeseries.csv',
     'UL-PUR_N20-NA6_18650_NCA_23C_0-100_0.5-0.5C_f_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-NA6_18650_NCA_23C_0-100_0.5-0.5C_f_cycle_data.csv',
     'UL-PUR_N20-NA6_18650_NCA_23C_0-100_0.5-0.5C_f_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-OV1_18650_NCA_23C_0-100_0.5-0.5C_a_timeseries.csv',
     'UL-PUR_N20-OV1_18650_NCA_23C_0-100_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_N20-OV1_18650_NCA_23C_0-100_0.5-0.5C_a_cycle_data.csv',
     'UL-PUR_N20-OV1_18650_NCA_23C_0-100_0.5-0.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R10-EX6_18650_NCA_23C_2.5-96.5_0.5-0.5C_f_timeseries.csv',
     'UL-PUR_R10-EX6_18650_NCA_23C_2.5-96.5_0.5-0.5C_f_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R10-EX6_18650_NCA_23C_2.5-96.5_0.5-0.5C_f_cycle_data.csv',
     'UL-PUR_R10-EX6_18650_NCA_23C_2.5-96.5_0.5-0.5C_f_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R10-NA11_18650_NCA_23C_2.5-96.5_0.5-0.5C_k_timeseries.csv',
     'UL-PUR_R10-NA11_18650_NCA_23C_2.5-96.5_0.5-0.5C_k_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R10-NA11_18650_NCA_23C_2.5-96.5_0.5-0.5C_k_cycle_data.csv',
     'UL-PUR_R10-NA11_18650_NCA_23C_2.5-96.5_0.5-0.5C_k_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R10-OV5_18650_NCA_23C_2.5-96.5_0.5-0.5C_e_timeseries.csv',
     'UL-PUR_R10-OV5_18650_NCA_23C_2.5-96.5_0.5-0.5C_e_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R10-OV5_18650_NCA_23C_2.5-96.5_0.5-0.5C_e_cycle_data.csv',
     'UL-PUR_R10-OV5_18650_NCA_23C_2.5-96.5_0.5-0.5C_e_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R15-EX4_18650_NCA_23C_2.5-96.5_0.5-0.5C_d_timeseries.csv',
     'UL-PUR_R15-EX4_18650_NCA_23C_2.5-96.5_0.5-0.5C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R15-EX4_18650_NCA_23C_2.5-96.5_0.5-0.5C_d_cycle_data.csv',
     'UL-PUR_R15-EX4_18650_NCA_23C_2.5-96.5_0.5-0.5C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R15-NA10_18650_NCA_23C_2.5-96.5_0.5-0.5C_j_timeseries.csv',
     'UL-PUR_R15-NA10_18650_NCA_23C_2.5-96.5_0.5-0.5C_j_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R15-NA10_18650_NCA_23C_2.5-96.5_0.5-0.5C_j_cycle_data.csv',
     'UL-PUR_R15-NA10_18650_NCA_23C_2.5-96.5_0.5-0.5C_j_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R15-OV3_18650_NCA_23C_2.5-96.5_0.5-0.5C_c_timeseries.csv',
     'UL-PUR_R15-OV3_18650_NCA_23C_2.5-96.5_0.5-0.5C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R15-OV3_18650_NCA_23C_2.5-96.5_0.5-0.5C_c_cycle_data.csv',
     'UL-PUR_R15-OV3_18650_NCA_23C_2.5-96.5_0.5-0.5C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-EX2_18650_NCA_23C_2.5-96.5_0.5-0.5C_b_timeseries.csv',
     'UL-PUR_R20-EX2_18650_NCA_23C_2.5-96.5_0.5-0.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-EX2_18650_NCA_23C_2.5-96.5_0.5-0.5C_b_cycle_data.csv',
     'UL-PUR_R20-EX2_18650_NCA_23C_2.5-96.5_0.5-0.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-NA7_18650_NCA_23C_2.5-96.5_0.5-0.5C_g_timeseries.csv',
     'UL-PUR_R20-NA7_18650_NCA_23C_2.5-96.5_0.5-0.5C_g_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-NA7_18650_NCA_23C_2.5-96.5_0.5-0.5C_g_cycle_data.csv',
     'UL-PUR_R20-NA7_18650_NCA_23C_2.5-96.5_0.5-0.5C_g_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-NA8_18650_NCA_23C_2.5-96.5_0.5-0.5C_h_timeseries.csv',
     'UL-PUR_R20-NA8_18650_NCA_23C_2.5-96.5_0.5-0.5C_h_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-NA8_18650_NCA_23C_2.5-96.5_0.5-0.5C_h_cycle_data.csv',
     'UL-PUR_R20-NA8_18650_NCA_23C_2.5-96.5_0.5-0.5C_h_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-NA9_18650_NCA_23C_2.5-96.5_0.5-0.5C_i_timeseries.csv',
     'UL-PUR_R20-NA9_18650_NCA_23C_2.5-96.5_0.5-0.5C_i_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-NA9_18650_NCA_23C_2.5-96.5_0.5-0.5C_i_cycle_data.csv',
     'UL-PUR_R20-NA9_18650_NCA_23C_2.5-96.5_0.5-0.5C_i_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-OV1_18650_NCA_23C_2.5-96.5_0.5-0.5C_a_timeseries.csv',
     'UL-PUR_R20-OV1_18650_NCA_23C_2.5-96.5_0.5-0.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/UL-PUR_R20-OV1_18650_NCA_23C_2.5-96.5_0.5-0.5C_a_cycle_data.csv',
     'UL-PUR_R20-OV1_18650_NCA_23C_2.5-96.5_0.5-0.5C_a_cycle_data.csv'),
)

HNEI_LINKS = (
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_c_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_c_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_d_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_d_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_e_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_e_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_e_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_e_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_f_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_f_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_f_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_f_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_g_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_g_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_g_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_g_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_j_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_j_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_j_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_j_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_l_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_l_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_l_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_l_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_m_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_m_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_m_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_m_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_n_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_n_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_n_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_n_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_o_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_o_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_o_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_o_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_p_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_p_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_p_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_p_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_s_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_s_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_s_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_s_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_t_timeseries.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_t_timeseries.csv'),
    ('https://www.batteryarchive.org/data/HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_t_cycle_data.csv',
     'HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_t_cycle_data.csv'),
)

OX_LINKS = (
    ('https://www.batteryarchive.org/data/OX_1-1_pouch_LCO_40C_0-100_2-1.84C_a_timeseries.csv',
     'OX_1-1_pouch_LCO_40C_0-100_2-1.84C_a_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-1_pouch_LCO_40C_0-100_2-1.84C_a_cycle_data.csv',
     'OX_1-1_pouch_LCO_40C_0-100_2-1.84C_a_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-2_pouch_LCO_40C_0-100_2-1.84C_b_timeseries.csv',
     'OX_1-2_pouch_LCO_40C_0-100_2-1.84C_b_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-2_pouch_LCO_40C_0-100_2-1.84C_b_cycle_data.csv',
     'OX_1-2_pouch_LCO_40C_0-100_2-1.84C_b_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-3_pouch_LCO_40C_0-100_2-1.84C_c_timeseries.csv',
     'OX_1-3_pouch_LCO_40C_0-100_2-1.84C_c_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-3_pouch_LCO_40C_0-100_2-1.84C_c_cycle_data.csv',
     'OX_1-3_pouch_LCO_40C_0-100_2-1.84C_c_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-4_pouch_LCO_40C_0-100_2-1.84C_d_timeseries.csv',
     'OX_1-4_pouch_LCO_40C_0-100_2-1.84C_d_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-4_pouch_LCO_40C_0-100_2-1.84C_d_cycle_data.csv',
     'OX_1-4_pouch_LCO_40C_0-100_2-1.84C_d_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-5_pouch_LCO_40C_0-100_2-1.84C_e_timeseries.csv',
     'OX_1-5_pouch_LCO_40C_0-100_2-1.84C_e_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-5_pouch_LCO_40C_0-100_2-1.84C_e_cycle_data.csv',
     'OX_1-5_pouch_LCO_40C_0-100_2-1.84C_e_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-6_pouch_LCO_40C_0-100_2-1.84C_f_timeseries.csv',
     'OX_1-6_pouch_LCO_40C_0-100_2-1.84C_f_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-6_pouch_LCO_40C_0-100_2-1.84C_f_cycle_data.csv',
     'OX_1-6_pouch_LCO_40C_0-100_2-1.84C_f_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-7_pouch_LCO_40C_0-100_2-1.84C_g_timeseries.csv',
     'OX_1-7_pouch_LCO_40C_0-100_2-1.84C_g_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-7_pouch_LCO_40C_0-100_2-1.84C_g_cycle_data.csv',
     'OX_1-7_pouch_LCO_40C_0-100_2-1.84C_g_cycle_data.csv'),
    ('https://www.batteryarchive.org/data/OX_1-8_pouch_LCO_40C_0-100_2-1.84C_h_timeseries.csv',
     'OX_1-8_pouch_LCO_40C_0-100_2-1.84C_h_timeseries.csv'),
    ('https://www.batteryarchive.org/data/OX_1-8_pouch_LCO_40C_0-100_2-1.84C_h_cycle_data.csv',
     'OX_1-8_pouch_LCO_40C_0-100_2-1.84C_h_cycle_data.csv'),
)

RWTH_LINKS = (
    ('https://publications.rwth-aachen.de/record/818642/files/Rawdata.zip',
     'raw.zip'),
)

KIT_UBC_LINKS = (
    ('https://zenodo.org/record/6405084/files/Dataset_1_NCA_battery.zip?download=1',
     'NCA.zip'),
    ('https://zenodo.org/record/6405084/files/Dataset_2_NCM_battery.zip?download=1',
     'NMC.zip'),
    ('https://zenodo.org/record/6405084/files/Dataset_3_NCM_NCA_battery.zip?download=1',
     'NMC_NCA.zip'),
    ('https://zenodo.org/record/6405084/files/Impedance%20raw%20data%20and%20fitting%20data.zip?download=1',
     'impedance.zip')
)


def get_links():
    return {
        # NOTE: batteryarchive.com stops their download service. For OX, SNL,
        #       HNEI, UL_PUR datasets, please contact them for access.
        # 'OX': OX_LINKS,
        # 'SNL': SNL_LINKS,
        'HUST': HUST_LINKS,
        'MATR': MATR_LINKS,
        # 'HNEI': HNEI_LINKS,
        'CALCE': CALCE_LINKS,
        'RWTH': RWTH_LINKS,
        # 'UL_PUR': UL_PUR_LINKS,
        # 'KIT_UBC': KIT_UBC_LINKS,
        'KIT_FOBOSS': KIT_FOBOSS_LINKS,
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