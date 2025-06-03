import os
import subprocess

ls = ["02_Aminobutyric-acid_zwitterion", "04_Aminobutyric-acid_zwitterion",
"01_Alanine_zwitterion", "07_Aminobutyric-acid_zwitterion",
"02_Alanine_zwitterion"]
for i in ls:
    os.chdir(i)
    os.chdir("packmol_outputs")
# 현재 디렉토리
    current_dir = os.getcwd()

# 상위 디렉토리의 output_pdb 경로
    output_dir = os.path.abspath(os.path.join(current_dir, '..', 'output_pdb'))

# output_pdb 폴더가 없으면 생성
    os.makedirs(output_dir, exist_ok=True)

# 모든 .xyz 파일 찾기
    xyz_files = [f for f in os.listdir(current_dir) if f.endswith('.xyz')]

# 변환 작업 수행
    for xyz_file in xyz_files:
        base_name = os.path.splitext(xyz_file)[0]
        input_path = os.path.join(current_dir, xyz_file)
        output_path = os.path.join(output_dir, f"{base_name}.pdb")
    
    # obabel 명령 실행
        result = subprocess.run(
        ['obabel', input_path, '-O', output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )

        if result.returncode == 0:
            print(f"✅ 변환 성공: {xyz_file} → {output_path}")
        else:
            print(f"❌ 변환 실패: {xyz_file}\n{result.stderr}")
    os.chdir("../../")
    print("\n🎉 전체 변환 완료.")

