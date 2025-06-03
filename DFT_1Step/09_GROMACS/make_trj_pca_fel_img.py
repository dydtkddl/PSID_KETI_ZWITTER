import os
import subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re

def run_command_with_input(cmd_list, user_input):
    process = subprocess.Popen(
        cmd_list,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    stdout, _ = process.communicate(input=user_input)
    print(stdout)
    if process.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd_list)}")

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def plot_fel_xpm(xpm_path, output_path="fel_xpm.png"):
    with open(xpm_path, "r") as f:
        string = f.read()

    lis = string.strip().split("\n")
    las = [i for i, x in enumerate(lis) if "/* x-axis:" in x]
    data_start = [i for i, x in enumerate(lis) if "/* y-axis:" in x][0] + 1
    colors = lis[lis.index("static char *gromacs_xpm[] = {") + 2 : las[0]]
    data = lis[data_start:]

    xticks = [float(x) for x in lis[las[0]].split(" ")[3:-1]]
    yticks = [float(x) for x in lis[las[0]+1].split(" ")[3:-1]]

    color_map = {}
    for line in colors:
        char, hex_color = line[1], line.split("#")[1].split('"')[0].strip()
        color_map[char.strip()] = hex_to_rgb(hex_color)

    height = len(data)
    width = len(data[0].strip('"'))
    rgb_array = np.zeros((height, width, 3))
    for i, line in enumerate(data):
        chars = line.strip().strip('"')
        for j, char in enumerate(chars):
            rgb_array[i, j] = color_map.get(char, (0, 0, 0))

    plt.figure(figsize=(6, 6))
    plt.imshow(rgb_array, origin='lower',
               extent=[xticks[0], xticks[-1], yticks[0], yticks[-1]],
               aspect='auto')
    plt.title("Free Energy Landscape (from XPM)")

    x_tick_idx = np.linspace(0, len(xticks) - 1, 6, dtype=int)
    y_tick_idx = np.linspace(0, len(yticks) - 1, 6, dtype=int)

    plt.xticks([xticks[i] for i in x_tick_idx],
               [f"{xticks[i]:.1e}" for i in x_tick_idx], rotation=45)
    plt.yticks([yticks[i] for i in y_tick_idx],
               [f"{yticks[i]:.1e}" for i in y_tick_idx])
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Saved plot: {output_path}")

def process_one_directory(folder_path):
    os.chdir(folder_path)
    print(f"\n📁 Processing: {folder_path}")

    try:
        run_command_with_input(["gmx", "make_ndx", "-f", "md.tpr", "-o", "index.ndx"], "0\nq\n")
        run_command_with_input(["gmx", "covar", "-s", "md.tpr", "-f", "coords.xtc",
                                "-n", "index.ndx", "-o", "eigenval.xvg",
                                "-v", "eigenvec.trr", "-av", "average.pdb"], "0\n0\n")
        run_command_with_input(["gmx", "anaeig", "-v", "eigenvec.trr", "-f", "coords.xtc",
                                "-s", "md.tpr", "-n", "index.ndx",
                                "-first", "1", "-last", "2", "-2d", "2dproj.xvg"], "0\n0\n")
        run_command_with_input(["gmx", "sham", "-f", "2dproj.xvg", "-ls", "fel.xpm", "-tsham", "300", "-notime"], "")
    except RuntimeError as e:
        print(f"❌ GROMACS step failed: {e}")
        return

    if Path("fel.xpm").exists():
        try:
            plot_fel_xpm("fel.xpm")
        except Exception as e:
            print(f"⚠️ Plotting failed: {e}")
    else:
        print("❗ fel.xpm not found, skipping plot.")

def main():
    root = Path.cwd()
    all_dirs = sorted([d for d in root.iterdir() if d.is_dir()])
    for d in all_dirs:
        try:
            process_one_directory(d)
        except Exception as e:
            print(f"❌ Failed on {d}: {e}")

if __name__ == "__main__":
    main()

