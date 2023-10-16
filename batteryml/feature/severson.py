# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import torch
import numpy as np

from numba import njit
from typing import List
from scipy.interpolate import interp1d
from sklearn.linear_model import LinearRegression

from batteryml.data.battery_data import BatteryData
from batteryml.feature.base import BaseFeatureExtractor


def interpolate(x, y, interp_dims, xs=0, xe=1):
    if len(x) <= 2:
        return np.zeros(interp_dims)
    func = interp1d(x, y, bounds_error=False)
    new_x = np.linspace(xs, xe, interp_dims)
    return func(new_x)


def _get_Qdlin(I, V, Q, min_V, max_V):  # noqa
    eps = 1e-1
    I, V, Q = np.array(I), np.array(V), np.array(Q)
    y = interpolate(V[I < -eps], Q[I < -eps], 1000, xs=min_V, xe=max_V)
    return y[::-1]


def get_Qdlin(cell_data, cycle_data, use_precalculated=False):
    if 'Qdlin' in cycle_data.additional_data and use_precalculated:
        return np.array(cycle_data.additional_data['Qdlin'])
    return _get_Qdlin(
        cycle_data.current_in_A,
        cycle_data.voltage_in_V,
        cycle_data.discharge_capacity_in_Ah,
        cell_data.min_voltage_limit_in_V,
        cell_data.max_voltage_limit_in_V)


@njit
def smooth(x, window_size=10, sigma=3):
    res = np.empty_like(x)
    meds = np.empty_like(x)
    for i in range(len(x)):
        low = max(0, i-window_size)
        high = min(len(x), i+window_size+1)
        meds[i] = np.median(x[low: high])
    base = np.std(np.abs(x - meds))
    for i in range(len(x)):
        if np.abs(meds[i] - x[i]) > base * sigma:
            res[i] = meds[i]
        else:
            res[i] = x[i]
    return meds


@njit
def get_charge_time(I, t):  # noqa
    res = 0.
    for i in range(1, len(I)):
        if I[i] < 0:
            res += t[i] - t[i-1]
    return res


class SeversonFeatureExtractor(BaseFeatureExtractor):
    def __init__(self,
                 interp_dims: int = 1000,
                 critical_cycles: List[int] = None,
                 smooth_diff_qdlin: bool = True,
                 use_precalculated_qdlin: bool = False):
        BaseFeatureExtractor.__init__(self)
        critical_cycles = critical_cycles or [1, 9, 99]
        self.interp_dims = interp_dims
        self.critical_cycles = sorted(critical_cycles)
        self.smooth_diff_qdlin = smooth_diff_qdlin
        self.use_precalculated_qdlin = use_precalculated_qdlin

    def get_features(self,
                     cell_data: BatteryData,
                     feature_lists: List[str]
                     ) -> torch.Tensor:
        early_cycle = cell_data.cycle_data[self.critical_cycles[1]]
        late_cycle = cell_data.cycle_data[self.critical_cycles[2]]

        early_qdlin = get_Qdlin(
            cell_data, early_cycle, self.use_precalculated_qdlin)
        late_qdlin = get_Qdlin(
            cell_data, late_cycle, self.use_precalculated_qdlin)

        diff_qdlin = late_qdlin - early_qdlin
        if self.smooth_diff_qdlin:
            diff_qdlin = smooth(diff_qdlin)
        diff_qdlin = torch.from_numpy(diff_qdlin)
        diff_qdlin = diff_qdlin[~diff_qdlin.isnan()]
        if len(diff_qdlin) <= 1:
            raise ValueError('Qdlin is all nan!')

        results = []
        for feature in feature_lists:
            value = self.get_feature(cell_data, diff_qdlin, feature)
            if value is not None:
                results.append(value)

        results = torch.tensor(results)

        # Fill NaN and Inf
        results[torch.isnan(results) | torch.isinf(results)] = 0.

        return results

    def get_feature(self,
                    cell_data: BatteryData,
                    diff_qdlin: torch.Tensor,
                    feature: str) -> float:
        eps = 1e-8
        # delta Qd features
        Qd_features = {
            'Minimum': lambda x: (x.min().abs() + eps).log10(),
            'Variance': lambda x: (x.var() + eps).log10(),
            'Skewness': lambda x: (
                ((x - x.mean()) ** 3).mean().abs() / (x.std() ** 3 + eps) + eps
            ).log10(),
            'Kurtosis': lambda x: (
                ((x - x.mean()) ** 4).mean() / (x.var() ** 2 + eps) + eps
            ).log10(),
        }
        if feature in Qd_features:
            result = Qd_features[feature](diff_qdlin).item()
            return result

        # Discharge capacity fade curve features
        Qd = [max(x.discharge_capacity_in_Ah) for x in cell_data.cycle_data]
        Qd = Qd[self.critical_cycles[0]: self.critical_cycles[2]]
        if feature == 'Early discharge capacity':
            return Qd[self.critical_cycles[0]]
        if feature == 'Difference between max discharge capacity and early discharge capacity':  # noqa
            return max(Qd) - Qd[self.critical_cycles[0]]
        if feature == 'Slope of linear fit to the capacity curve':
            model = LinearRegression()
            x, y = np.arange(len(Qd))[:, None], np.array(Qd)
            model.fit(x, y)
            return model.coef_[0]
        if feature == 'Intercept of linear fit to the capacity curve':
            model = LinearRegression()
            x, y = np.arange(len(Qd))[:, None], np.array(Qd)
            model.fit(x, y)
            return model.intercept_

        # Other features
        if feature == 'Average early charge time':
            charge_time = []
            for cycle in range(4):
                cycle_data = cell_data.cycle_data[cycle]
                if cycle_data.time_in_s is not None:
                    charge_time.append(get_charge_time(
                        np.array(cycle_data.current_in_A),
                        np.array(cycle_data.time_in_s)
                    ))
            result = np.mean(charge_time) if len(charge_time) else 0.
            return np.log(result + eps)
        if feature == 'Integral of temperature over time':
            res, counts = 0., 0
            for cycle in range(self.critical_cycles[0],
                               self.critical_cycles[2] + 1):
                cycle_data = cell_data.cycle_data[cycle]
                if cycle_data.temperature_in_C is not None:
                    T = [x for x in cycle_data.temperature_in_C if x == x]
                    if len(T):
                        res += np.nanmean(cycle_data.temperature_in_C)
                        counts += 1
            if counts > 0:
                res /= counts
            result = np.log(res + eps)
            return result
        if feature == 'Minimum internal resistance':
            ir = []
            for cycle in range(self.critical_cycles[0],
                               self.critical_cycles[2] + 1):
                cycle_data = cell_data.cycle_data[cycle]
                if cycle_data.internal_resistance_in_ohm is not None:
                    ir.append(cycle_data.internal_resistance_in_ohm)
            return np.min(ir) if len(ir) else 0.
        if feature == 'Internal resistance change':
            early_ir = cell_data.cycle_data[self.critical_cycles[0]]\
                .internal_resistance_in_ohm
            late_ir = cell_data.cycle_data[self.critical_cycles[2]]\
                .internal_resistance_in_ohm
            if early_ir is not None and late_ir is not None:
                return late_ir - early_ir
            return 0.
