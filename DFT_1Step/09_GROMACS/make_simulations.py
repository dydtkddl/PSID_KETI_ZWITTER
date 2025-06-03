import os
import shutil
from pathlib import Path
import argparse

def setup_simulation_dirs(sorted_pdb_dir, basedir):
    # 절대 경로로 변환
    sorted_pdb_dir = Path(sorted_pdb_dir).resolve()
    basedir = Path(basedir).resolve()
    simulations_dir = Path.cwd() / "simulations"
    
    # simulations 디렉토리 생성
    simulations_dir.mkdir(exist_ok=True)
    
    # .pdb 파일 목록 가져오기
    pdb_files = list(sorted_pdb_dir.glob("*.pdb"))
    if not pdb_files:
        print(f"⚠️ No PDB files found in {sorted_pdb_dir}")
        return

    # basedir의 *.mdp 파일 가져오기
    mdp_files = list(basedir.glob("*.mdp"))
    if not mdp_files:
        print(f"⚠️ No MDP files found in {basedir}")
        return

    for pdb_path in pdb_files:
        name = pdb_path.stem
        sim_subdir = simulations_dir / name
        sim_subdir.mkdir(exist_ok=True)

        # pdb 파일 복사
        shutil.copy(pdb_path, sim_subdir / pdb_path.name)

        # mdp 파일들 복사
        for mdp_file in mdp_files:
            shutil.copy(mdp_file, sim_subdir / mdp_file.name)

        print(f"✅ Created: {sim_subdir} with {pdb_path.name} and {len(mdp_files)} .mdp files")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate simulation directories from PDB and MDP sources.")
    parser.add_argument("sorted_pdb_dir", help="Directory containing sorted PDB files")
    parser.add_argument("basedir", help="Directory containing MDP template files")

    args = parser.parse_args()
    setup_simulation_dirs(args.sorted_pdb_dir, args.basedir)

