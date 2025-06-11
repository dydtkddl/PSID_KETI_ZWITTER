#!/bin/bash

# 명시적으로 지정된 디렉토리 리스트
dirs=(
  "00_Aminobutyric-acid_zwitterion"
  "01_Alanine_zwitterion"
  "02_Alanine_zwitterion"
  "02_Aminobutyric-acid_zwitterion"
  "04_Aminobutyric-acid_zwitterion"
  "07_Aminobutyric-acid_zwitterion"
)

# 각 디렉토리에 대해 작업 수행
for dir in "${dirs[@]}"; do
  postdir="${dir}/post"
  
  if [ -d "$postdir" ]; then
    echo "▶ Entering $postdir"
    cd "$postdir" || continue

    # removewater.xyz → input.xyz 복사
    if [ -f removewater.xyz ]; then
      cp -rf removewater.xyz input.xyz
      echo "✓ Copied removewater.xyz to input.xyz"
    else
      echo "✗ removewater.xyz not found in $postdir"
    fi

    # orca_plot_auto.sh 실행
    if [ -f ../../orca_plot_auto.sh ]; then
      nohup sh ../../orca_plot_auto.sh input.gbw > orcaplot.log 2>&1 &
      echo "✓ orca_plot_auto.sh launched in background"
    else
      echo "✗ ../../orca_plot_auto.sh not found"
    fi

    # 원래 디렉토리로 복귀
    cd - > /dev/null
  else
    echo "✗ $postdir does not exist"
  fi
done

echo "✅ 모든 작업 완료"

