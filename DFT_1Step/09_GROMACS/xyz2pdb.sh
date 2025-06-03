#!/bin/bash

# 상위 디렉토리에 output_pdb 폴더 생성 (없으면)
mkdir -p ../output_pdb

# 현재 디렉토리의 모든 .xyz 파일에 대해
for file in *.xyz; do
    # 파일 이름에서 확장자 제거
    base=$(basename "$file" .xyz)

    # obabel 변환: output_pdb에 .pdb 파일로 저장
    obabel "$file" -O "../output_pdb/${base}.pdb"
done

echo "✅ 변환 완료: output_pdb 폴더에 PDB 파일 저장됨"

