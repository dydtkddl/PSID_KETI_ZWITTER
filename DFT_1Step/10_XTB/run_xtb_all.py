import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_xtb_all(input_dir, output_dir_name):
    input_dir = Path(input_dir)
    output_root = Path.cwd() / output_dir_name

    if not input_dir.exists():
        print(f"❌ 입력 디렉토리가 존재하지 않습니다: {input_dir}")
        sys.exit(1)

    output_root.mkdir(exist_ok=True)
    log_path = output_root / "progress.log"

    xyz_files = list(input_dir.glob("*.xyz"))
    total = len(xyz_files)
    if total == 0:
        print(f"❌ .xyz 파일이 없습니다: {input_dir}")
        sys.exit(1)

    with open(log_path, "w") as log:
        log.write(f"[ XTB Batch Run Started ]\nTotal files: {total}\n\n")

        for i, xyz_path in enumerate(xyz_files, start=1):
            name = xyz_path.stem
            target_dir = output_root / name
            target_dir.mkdir(exist_ok=True)

            dst_xyz = target_dir / xyz_path.name
            shutil.copy2(xyz_path, dst_xyz)

            progress_msg = f"[{i}/{total}] ▶ {name} 처리 중..."
            print(progress_msg)
            log.write(progress_msg + "\n")

            try:
                subprocess.run(
                    ["xtb", xyz_path.name, "--opt", "tight", "--gfn", "2", "--chrg", "0", "--uhf", "0", "--alpb", "water"],
                    cwd=target_dir,
                    check=True
                )
                result_msg = f"[{i}/{total}] ✅ {name} 최적화 완료"
            except subprocess.CalledProcessError:
                result_msg = f"[{i}/{total}] ❌ {name} 최적화 실패"

            print(result_msg)
            log.write(result_msg + "\n")

        log.write("\n[ XTB Batch Run Completed ]\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python run_xtb_all.py [packmol_output 디렉토리] [output 디렉토리 이름]")
        sys.exit(1)

    run_xtb_all(sys.argv[1], sys.argv[2])
