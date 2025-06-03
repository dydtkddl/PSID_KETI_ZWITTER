import os
from tqdm import tqdm

# 하위 디렉토리 중 폴더만 필터링
directories = [d for d in os.listdir() if os.path.isdir(d) and "ex" not in d]

SEQ = ""
for folder in directories:
    print(folder)
    # RESIDUE 이름 지정 조건
    if "Alan" in folder:
        RESIDUE = "BAL"
        SEQ = "N,H1,H2,H3,CA,HA1,HA2,CB,HB1,HB2,C,O1,O2"
    else:
        RESIDUE = "AMB"
        SEQ = "N,H1,H2,H3,CA,HA1,HA2,CB,HB1,HB2,CC,HC1,HC2,C,O1,O2"
    os.chdir(folder)

    # PDB 파일 리스트 수집
    pdbs = [f for f in os.listdir("output_pdb") if f.endswith(".pdb")]

    # 정렬된 파일 저장할 디렉토리 생성
    os.makedirs("sorted_pdb", exist_ok=True)
    os.chdir("sorted_pdb")
    for pdb in tqdm( pdbs):
        input_path = os.path.join("../output_pdb", pdb)
        command = f"python ../../pdb_sort.py {input_path} {RESIDUE} {SEQ}"
        os.system(command)

    os.chdir("../..")

