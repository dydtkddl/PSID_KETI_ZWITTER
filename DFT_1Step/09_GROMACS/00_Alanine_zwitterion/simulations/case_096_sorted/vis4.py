import numpy as np
import matplotlib.pyplot as plt
import re  # 추가

def read_xpm(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # 1. Find size line
    for i, line in enumerate(lines):
        if line.strip().startswith('"') and line.strip().strip('"').split()[0].isdigit():
            size_line = line.strip().strip(',').strip('"')
            print(size_line)
            width, height, num_colors, num_chars = map(int, size_line.split())
            data_start = i
            break

    # 2. Read color definitions
    color_map = {}
    for j in range(num_colors):
        line = lines[data_start + 1 + j].strip().rstrip(',')
        parts = line.split('"')
        key = parts[1]
        # 🔽 정규표현식으로 숫자만 추출
        match = re.search(r'"([\d\.\-eE]+)"', line)
        if match:
            val = float(match.group(1))
        else:
            raise ValueError(f"Cannot parse value from: {line}")
        color_map[key] = val

    # 3. Read pixel matrix
    matrix_lines = lines[data_start + 1 + num_colors : data_start + 1 + num_colors + height]

        # 3. Read only valid pixel lines (start with quote)
    matrix = []
    for line in lines[data_start + 1 + num_colors:]:
        if line.strip().startswith('"'):
            pixels = line.strip().strip('"').strip(',')  # remove quotes, commas
            if len(pixels) == 0: continue  # skip empty
            row = [color_map[pixels[i:i+num_chars]] for i in range(0, len(pixels), num_chars)]
            matrix.append(row)
        else:
            break  # stop if line is not a pixel line

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

