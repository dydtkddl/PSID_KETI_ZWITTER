import numpy as np
import matplotlib.pyplot as plt

def read_xpm(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # 1. Find line with dimensions: e.g., "32 32 25 1",
    for i, line in enumerate(lines):
        if line.strip().startswith('"') and line.strip().strip('"').split()[0].isdigit():
            size_line = line.strip().strip(',').strip('"')  # "32 32 25 1",
            print(size_line)
            width, height, num_colors, num_chars = map(int, size_line.split())
            data_start = i
            break

    # 2. Read color definitions
    color_map = {}
    for j in range(num_colors):
        line = lines[data_start + 1 + j].strip().rstrip(',')  # Remove trailing comma
        parts = line.split('"')
        key = parts[1]  # color character
        print(parts)
        val = float(parts[2].split()[-1])  # value from comment e.g., /* "1.23" */
        color_map[key] = val

    # 3. Read pixel matrix
    matrix_lines = lines[data_start + 1 + num_colors : data_start + 1 + num_colors + height]
    matrix = []
    for line in matrix_lines:
        pixels = line.strip().strip('"').strip(',')  # remove quotes and comma
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

