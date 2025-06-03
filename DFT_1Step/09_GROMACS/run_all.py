import os
import subprocess
from pathlib import Path
import argparse

def find_pdb_file(directory):
    pdb_files = list(Path(directory).glob("*.pdb"))
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

def run_gromacs_pipeline(sim_dir, nt):
    os.chdir(sim_dir)
    print(f"\n📂 Entering directory: {sim_dir}")

    pdb_file = find_pdb_file(".")
    if not pdb_file:
        print("❌ No .pdb file found. Skipping.")
        return False

    try:
        run_command(f"gmx pdb2gmx -f {pdb_file} -o processed.gro -p topol.top -ff oplsaa -water tip3p -ter")
        run_command("gmx editconf -f processed.gro -o newbox.gro -c -d 1.0 -bt cubic")
        run_command("gmx grompp -f em.mdp -c newbox.gro -p topol.top -o em.tpr -maxwarn 1")
        run_command(f"gmx mdrun -deffnm em -nt {nt}")
        run_command("gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 1")
        run_command(f"gmx mdrun -deffnm nvt -nt {nt}")
        run_command("gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -maxwarn 1")
        run_command(f"gmx mdrun -deffnm npt -nt {nt}")
        run_command("gmx grompp -f md.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o md.tpr -maxwarn 2")
        run_command(f"gmx mdrun -deffnm md -v -nt {nt}")
        print("✅ Finished simulation.")
        return True
    except RuntimeError:
        print("⚠️ Aborted due to error.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run GROMACS workflow in all subdirectories.")
    parser.add_argument("--nt", "-n", type=int, default=25, help="Number of threads for mdrun (default: 25)")
    args = parser.parse_args()

    current_dir = Path.cwd()
    all_dirs = sorted([d for d in current_dir.iterdir() if d.is_dir()])
    total = len(all_dirs)
    completed_count = 0

    with open("completed.txt", "w") as completed_file:
        for i, folder in enumerate(all_dirs, 1):
            success = False
            try:
                success = run_gromacs_pipeline(folder, args.nt)
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
