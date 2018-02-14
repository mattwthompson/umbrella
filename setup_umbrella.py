import numpy as np


def find_nearest(distances, val):
    idx = (np.abs(distances[:, 1] - val)).argmin()
    return distances[idx, 0]


spacing = 0.02
distances = np.loadtxt('distance_summary.dat')

min_val = np.floor(np.min(distances[:, 1]) / spacing) * spacing
max_val = np.ceil(np.max(distances[:, 1]) / spacing) * spacing
num_val = 1 + int((max_val - min_val) / spacing)

print('#conf \t\tCOM distance')
for val in np.linspace(min_val, max_val, num_val):
    idx = find_nearest(distances, val)
    print(int(idx), '\t', round(val, 3))
