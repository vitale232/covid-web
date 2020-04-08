import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_rgbs(values, bins, colormap='viridis', mode='equalcount'):
    # Colormap currently supports perceptually uniform sequential
    # colormaps from matplotlib: 'viridis', 'plasma', 'inferno', 'magma', 'cividis'
    # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
    if mode == 'equalinterval':
        cuts = pd.cut(values, bins, duplicates='drop')
    else:
        # Default to equal count
        cuts = pd.qcut(values, bins, duplicates='drop')

    cuts_out = [list(cut) for cut in cuts.categories.to_tuples()]
    cuts_out[0][0] = float(np.min(values) - 0.001)
    cuts_out[-1][1] = float(np.max(values))

    cmap = plt.cm.get_cmap(colormap, len(cuts_out))
    cmap_colors = cmap.colors.tolist()

    colors_out = []
    for color in cmap_colors:
        colors_out.append([
            round(color[0] * 255),
            round(color[1] * 255),
            round(color[2] * 255),
        ])

    color_stats = {
        'input_params': {
            'bins': bins,
            'colormap': colormap,
            'mode': mode,
        },
        'cuts': {
            'intervals': cuts_out,
            'closed': cuts.categories.closed,
            'rgb_colors': colors_out,
        },
    }

    return color_stats
