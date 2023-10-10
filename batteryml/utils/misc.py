# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

from tqdm import tqdm


def tqdm_wrapper(iterable, *args, **kwargs):
    return tqdm(
        iterable,
        position=1,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
        *args, **kwargs)
