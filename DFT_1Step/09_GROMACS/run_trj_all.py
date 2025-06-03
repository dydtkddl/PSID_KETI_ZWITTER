import os
import subprocess
from pathlib import Path
import argparse

def find_md_trr_file(directory):
    pdb_files = list(Path(directory).glob("md.trr"))
    if not pdb_files:
        return None
    if len(pdb_files) > 1:
        print(f"⚠️ Multiple .pdb files in {directory}. Using {pdb_files[0].name}")
    return pdb_files[0].name

def run_command(cmd):
    print(f"▶️ {cmd}")
    process = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        raise RuntimeError(f"Command failed: {cmd}")

def run_gromacs_pipeline(sim_dir):
    os.chdir(sim_dir)
    print(f"\n📂 Entering directory: {sim_dir}")

    md_trr_file = find_md_trr_file(".")
    if not md_trr_file:
        print("❌ No md.trr file found. Skipping.")
        return False

    try:
        run_command(f"echo 0 | gmx traj -f md.trr -s md.tpr -oxt coords.xtc")
        print("✅ Finished simulation.")
        return True
    except RuntimeError:
        print("⚠️ Aborted due to error.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run GROMACS workflow in all subdirectories.")
    args = parser.parse_args()

    current_dir = Path.cwd()
    all_dirs = sorted([d for d in current_dir.iterdir() if d.is_dir()])
    total = len(all_dirs)
    completed_count = 0

    with open("croped_trj.txt", "w") as completed_file:
        for i, folder in enumerate(all_dirs, 1):
            success = False
            try:
                success = run_gromacs_pipeline(folder)
            except Exception as e:
                print(f"❗ Failed in {folder.name}: {e}")

            if success:
                completed_count += 1
                line = f"[{completed_count}/{total}] ✅ {folder.name}\n"
                completed_file.write(line)
                completed_file.flush()
                print(f"📄 {line.strip()}")

if __name__ == "__main__":
    main()
