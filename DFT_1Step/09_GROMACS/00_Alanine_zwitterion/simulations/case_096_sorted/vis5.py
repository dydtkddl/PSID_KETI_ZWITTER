import numpy as np
import matplotlib.pyplot as plt
import re
import matplotlib
matplotlib.use('Agg')  # GUI 창 없이 PNG로 저장만 가능
import re

def parse_xpm(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    color_map = {}
    data_lines = []
    color_section_done = False

    for line in lines:
        line = line.strip()
        # 색상 맵핑 줄 처리
        if not color_section_done and 'c #' in line and '/*' in line:
            match = re.search(r'^"(.+?)\s+c\s+#\S+"\s+/\*\s+"([\d\.\-eE\+]+)"\s+\*/,?$', line)
            if match:
                char, value = match.groups()
                color_map[char.strip()] = float(value)
        elif line.startswith('"') and line.endswith('"'):
            content = line.strip('"')
            if content:
                data_lines.append(content)
                color_section_done = True

    # 데이터 배열로 변환
    height = len(data_lines)
    width = len(data_lines[0])
    data = np.zeros((height, width))

    for i, line in enumerate(data_lines):
        for j, char in enumerate(line):
            data[i, j] = color_map.get(char, np.nan)

    return data

def plot_xpm_data(data, cmap='inferno'):
    plt.figure(figsize=(8, 6))
    plt.imshow(data, origin='lower', cmap=cmap, aspect='auto')
    plt.colorbar(label='Free Energy (kcal/mol or kJ/mol)')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Free Energy Landscape')
    plt.tight_layout()
    plt.savefig("FEL.png")


# 사용 예시
xpm_file = 'fel.xpm'
data = parse_xpm(xpm_file)
print(data)
plot_xpm_data(data)

