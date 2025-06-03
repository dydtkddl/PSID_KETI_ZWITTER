import numpy as np
import matplotlib.pyplot as plt

def read_xpm(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # 1. Find first non-comment line with dimensions info
    for i, line in enumerate(lines):
        if line.strip().startswith('"'):
            size_line = line.strip().strip('"').strip(',')  # "32 32 25 1",
            width, height, num_colors, num_chars = map(int, size_line.split())
            data_start = i
            break

    # 2. Read color definitions
    color_map = {}
    for j in range(num_colors):
        line = lines[data_start + 1 + j].strip().strip(',')
        key = line.split('"')[1]
        val = float(line.split('"')[2].split()[-1])
        color_map[key] = val

    # 3. Read matrix
    matrix_lines = lines[data_start + 1 + num_colors : data_start + 1 + num_colors + height]
    matrix = []
    for line in matrix_lines:
        pixels = line.strip().strip('"').strip(',')
        row = [color_map[pixels[i:i+num_chars]] for i in range(0, len(pixels), num_chars)]
        matrix.append(row)

    return np.array(matrix)

# --- 시각화 코드 ---
fel = read_xpm("fel.xpm")
plt.figure(figsize=(6,5))
plt.imshow(fel, origin='lower', cmap='plasma', aspect='auto')
plt.colorbar(label='Free Energy (kJ/mol)')
plt.title("Free Energy Landscape")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.tight_layout()
plt.show()

