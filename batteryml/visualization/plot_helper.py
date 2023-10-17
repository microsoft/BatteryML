# Licensed under the MIT License.
# Copyright (c) Microsoft Corporation.

import matplotlib.pyplot as plt
import numpy as np
def plot_capacity_degradation(battery_data,
                              figsize=(12, 12),
                              normalize=True,
                              title='',
                              n_legend_cols=3,
                              ylim=None):
    plt.figure(figsize=figsize)

    colors = plt.cm.jet(np.linspace(0, 1, len(battery_data)))

    for color, cell_data in zip(colors, battery_data):
        tag = cell_data.cell_id
        inner_plot_capacity_degradation(cell_data, normalize=normalize, color=color, label=f'{tag}')

    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", ncol=n_legend_cols)
    plt.grid()
    plt.title(title)
    plt.xlabel('Cycles')
    plt.ylabel('Capacity')
    if ylim:
        plt.ylim(ylim)



def inner_plot_capacity_degradation(cell_data,
                                    normalize=True,
                                    **kwargs):
    nominal_capacity = cell_data.nominal_capacity_in_Ah
    q_ds = [max(cycle.discharge_capacity_in_Ah) for cycle in cell_data.cycle_data]

    if normalize:
        q_ds = [ q_d/nominal_capacity for q_d in q_ds]
    x = np.arange(len(q_ds)) + 1
    plt.plot(x, q_ds, **kwargs)


def plot_cycle_attribute(cycle_infos,
                           key_fea,
                           figsize=(12, 4),
                           title='',
                           cycle_start=None,
                           cycle_end=None,
                           cycle_indices = None,
                           index_start=None,
                           index_end=None,
                           n_legend_cols=3,
                           x_feature = 'time_in_s',
                           fontsize='small',
                           markerscale=0.5):
    plt.figure(figsize=figsize)

    if cycle_indices:
        cycle_infos = [cycle_infos[i] for i in cycle_indices]
    else:
        cycle_infos = cycle_infos[cycle_start:cycle_end]

    length = len(cycle_infos)

    if key_fea == 'internal_resistance_in_ohm':
        y = [getattr(cycle_info, key_fea) for cycle_info in cycle_infos]
        x = [getattr(cycle_info, 'cycle_number') for cycle_info in cycle_infos]
        plt.plot(x, y)
        xlabel = 'cycle'

    if key_fea == 'coulombic_efficiency':
        # build coulombic_efficiency
        y = [max(cycle_info.discharge_capacity_in_Ah) / max(cycle_info.charge_capacity_in_Ah)  for cycle_info in cycle_infos]
        x = [getattr(cycle_info, 'cycle_number') for cycle_info in cycle_infos]
        plt.plot(x, y)
        xlabel = 'cycle'
    else:
        colors = plt.cm.jet(np.linspace(0, 1, length))

        for color, cycle_info in zip(colors, cycle_infos):

            y = getattr(cycle_info, key_fea)
            if isinstance(y, np.float64):
                continue
            if x_feature and  hasattr(cycle_info, x_feature):
                x = getattr(cycle_info, x_feature)
            else:
                x = [i for i in range(len(y))]

            plt.plot(x[index_start:index_end], y[index_start:index_end],color=color, label=f'Cycle {cycle_info.cycle_number}')
            plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", ncol=n_legend_cols, fontsize=fontsize, markerscale=markerscale)
            xlabel = x_feature
    plt.grid()
    plt.xlabel(xlabel)
    plt.ylabel(key_fea)
    plt.title(title)



def plot_result(ground_truth_y, y_pred):
    # normalized_y = (y - y.min()) / (y.max() - y.min()) 
    norm = plt.Normalize(ground_truth_y.min(), ground_truth_y.max())

    cmap = plt.get_cmap('viridis')
    plt.scatter(ground_truth_y, y_pred, c=ground_truth_y, cmap='viridis', norm=norm)
    cbar = plt.colorbar()
    # cbar.ax.set_title(r'$Q_n$'+' (Ah)', fontsize=7)
    # cbar.ax.invert_yaxis()
    cbar.set_label('Cycle life')

    # Generate data points for the 45-degree line
    x_line = np.linspace(ground_truth_y.min(), ground_truth_y.max(), 100)  
    y_line = x_line


    # Add the 45-degree line to the plot
    plt.plot(x_line, y_line,  color='grey')  # Customize line style and color as needed

    plt.xlabel('Ground Truth')
    plt.ylabel('Prediction')
    plt.legend()

    plt.show()

