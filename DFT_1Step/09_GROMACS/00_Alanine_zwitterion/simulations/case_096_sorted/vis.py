import numpy as np
import matplotlib.pyplot as plt

def read_xpm(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # 1. Skip all comments until we find the size definition
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('"'):
            data_start = i
            break

    # 2. Extract width, height, num_colors, num_chars from size line
    size_info = lines[data_start].strip().strip('"').split()
    width, height = int(size_info[0]), int(size_info[1])
    num_colors = int(size_info[2])
    num_chars = int(size_info[3])
    
    # 3. Read color map
    color_lines = lines[data_start+1 : data_start+1+num_colors]
    color_map = {}
    for line in color_lines:
        key = line.strip().split('"')[1]
        value = float(line.strip().split()[-1])
        color_map[key] = value

    # 4. Read pixel matrix
    matrix_lines = lines[data_start+1+num_colors : data_start+1+num_colors+height]
    matrix = []
    for line in matrix_lines:
        line_data = line.strip().strip('"')
        row = [color_map[line_data[i:i+num_chars]] for i in range(0, len(line_data), num_chars)]
        matrix.append(row)

    return np.array(matrix)
fel = read_xpm("fel.xpm")
plt.imshow(fel, origin='lower', cmap='plasma')
plt.colorbar(label='Free Energy (kJ/mol)')
plt.title("Free Energy Landscape")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.tight_layout()
plt.show()

