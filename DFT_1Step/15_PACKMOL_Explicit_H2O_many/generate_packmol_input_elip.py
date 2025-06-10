import os
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import combinations

# ===================================================================================
# Utility Functions
# ===================================================================================

def read_xyz_with_elements(filename):
    """
    XYZ 파일을 읽어 원자 종류와 좌표를 반환.
    [목적] 원자 단위 시각화를 위해 원소 정보도 함께 추출.
    """
    with open(filename) as f:
        lines = f.readlines()
    n_atoms = int(lines[0])
    elements = []
    coords = []
    for line in lines[2:2 + n_atoms]:
        parts = line.strip().split()
        elements.append(parts[0])
        x, y, z = map(float, parts[1:4])
        coords.append([x, y, z])
    return np.array(coords), elements

def center_coords(coords):
    """
    분자의 기하학적 중심을 원점으로 이동.
    [목적] 타원체 fitting 및 회전을 위한 기준 중심 정렬.
    """
    centroid = coords.mean(axis=0)
    centered = coords - centroid
    return centered, centroid, centroid

def compute_ellipsoid_axes(coords_centered):
    """
    중심 정렬된 좌표계에 대해 공분산 행렬을 기반으로 주축 방향과 축 길이 계산.
    [목적] 타원체 fitting과 분자 방향 정렬에 필요.
    """
    cov = np.cov(coords_centered.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    axes_lengths = 2 * np.sqrt(eigvals)  # 2σ 길이를 기반으로 한 semi-axis 추정
    return axes_lengths, eigvecs

def rotate_coords(coords, eigvecs):
    """
    주축 정렬을 위해 eigenvector 기반 좌표 회전 수행.
    [목적] Packmol의 타원체 제약이 축 기준이므로 분자의 방향을 정렬해 호환시킴.
    """
    return coords @ eigvecs  # 좌표 회전 (R·x)

def write_xyz(filename, coords, elements):
    """
    변환된 좌표와 원소 정보를 .xyz 파일로 저장.
    [목적] Packmol 입력에 사용할 회전된 중심 분자 저장용.
    """
    with open(filename, "w") as f:
        f.write(f"{len(coords)}\n")
        f.write("Rotated molecule\n")
        for e, (x, y, z) in zip(elements, coords):
            f.write(f"{e} {x:.6f} {y:.6f} {z:.6f}\n")

def draw_ellipsoid(ax, axes_lengths, margin, color='gray', alpha=0.2):
    """
    주어진 축 길이 + margin에 기반한 타원체 시각화.
    [목적] solvent 분자 제약 구간의 시각적 검증을 위해 필요.
    """
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 60)
    a, b, c = axes_lengths + margin
    x = a * np.outer(np.cos(u), np.sin(v))
    y = b * np.outer(np.sin(u), np.sin(v))
    z = c * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(x, y, z, color=color, alpha=alpha, linewidth=0.5)

def draw_bonds(ax, coords, elements, threshold=1.8):
    """
    두 원자 사이의 거리가 특정 임계값보다 짧으면 결합으로 간주하고 선 연결.
    [목적] 분자 구조 내 공유 결합을 시각적으로 나타냄.
    """
    for i, j in combinations(range(len(coords)), 2):
        dist = np.linalg.norm(coords[i] - coords[j])
        if dist < threshold:
            ax.plot(*zip(coords[i], coords[j]), color='gray', linewidth=0.8, alpha=0.6)

def get_color(element):
    """
    원자 종류에 따른 시각화 색상 지정.
    [목적] 원소별 분자 구조의 시각적 식별을 돕기 위해.
    """
    colors = {
        "H": "white", "C": "black", "N": "blue", "O": "red", "S": "yellow",
        "Cl": "green", "F": "cyan", "Br": "brown", "I": "purple"
    }
    return colors.get(element, "magenta")

# ===================================================================================
# 1. Config 불러오기 및 준비
# ===================================================================================

config_path = "config.json"
with open(config_path, 'r') as f:
    config = json.load(f)

center_file = config["center_molecule"]
solvents = config["solvent_molecules"]
base_name = config.get('base_name', 'case')
output_path = f"{base_name}.inp"
rotated_xyz_path = f"rotated_{os.path.basename(center_file)}"

# ===================================================================================
# 2. 중심 분자 회전 및 저장
# ===================================================================================

coords, elements = read_xyz_with_elements(center_file)
centered_coords, _, centroid = center_coords(coords)
axes_lengths, eigvecs = compute_ellipsoid_axes(centered_coords)
rotated_coords = rotate_coords(centered_coords, eigvecs)
write_xyz(rotated_xyz_path, rotated_coords, elements)

# ===================================================================================
# 3. Packmol base input 파일 생성
# ===================================================================================

with open(output_path, 'w') as f:
    f.write("tolerance 2.0\nfiletype xyz\noutput case_{index}.xyz\n\n")
    
    # 중심 분자 고정 배치
    f.write(f"structure ../{rotated_xyz_path}\n")
    f.write("  number 1\n  fixed 0. 0. 0. 0. 0. 0.\nend structure\n\n")
    
    # Solvent 분자에 대해 각기 다른 타원체 margin 설정
    for solvent in solvents:
        margin = solvent.get("ellipsoid_margin", 1.5)
        a, b, c = axes_lengths + margin
        f.write(f"structure ../{solvent['file']}\n")
        f.write(f"  number {solvent['count']}\n")
        f.write(f"  inside ellipsoid 0.0 0.0 0.0 {a:.4f} {b:.4f} {c:.4f} 1.0\n")
        f.write("end structure\n\n")

    # Seed와 초기 무작위 위치 설정
    f.write("seed {seed}\nrandominitialpoint\n")

# ===================================================================================
# 4. 3D 시각화 (중심분자 + 타원체)
# ===================================================================================

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 중심 분자 원자 표시
for coord, elem in zip(rotated_coords, elements):
    ax.scatter(*coord, color=get_color(elem), s=60, edgecolors='k', depthshade=True)

# 결합 표시
draw_bonds(ax, rotated_coords, elements)

# 기준 타원체 및 각 solvent margin 타원 표시
draw_ellipsoid(ax, axes_lengths, margin=0.0, color='black', alpha=0.1)
colors = ['green', 'orange', 'purple', 'cyan', 'brown']
for i, solvent in enumerate(solvents):
    margin = solvent.get("ellipsoid_margin", 1.5)
    draw_ellipsoid(ax, axes_lengths, margin=margin, color=colors[i % len(colors)], alpha=0.25)

# 그래프 라벨 설정
ax.set_title("Rotated Molecule + Aligned Ellipsoids")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

# 축 스케일을 가장 큰 ellipsoid 기준으로 고정
max_margin = max(solvent.get("ellipsoid_margin", 1.5) for solvent in solvents)
a, b, c = axes_lengths + max_margin
max_range = max(a, b, c)
ax.set_xlim(-max_range, max_range)
ax.set_ylim(-max_range, max_range)
ax.set_zlim(-max_range, max_range)

plt.tight_layout()
plt.savefig("./config.jpg")
# plt.show()
