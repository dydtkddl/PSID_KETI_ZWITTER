#!/bin/bash

# ORCA 실행 경로
ORCA=/home/ys/orca_6_0_1_linux_x86-64_shared_openmpi416/orca

# 각 노드와 해당 디렉터리 매핑
declare -a NODES=("psid00" "psid05" "psid06" "psid07" "psid08" "psid09" "psid10")
declare -a DIRS=(
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/00_Alanine_zwitterion/post"
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/01_Alanine_zwitterion/post"
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/02_Alanine_zwitterion/post"
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/00_Aminobutyric-acid_zwitterion/post"
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/02_Aminobutyric-acid_zwitterion/post"
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/04_Aminobutyric-acid_zwitterion/post"
"/home/ys/PSID_KETI_ZWITTER/DFT_1Step/19_PostProcess/07_Aminobutyric-acid_zwitterion/post"
)

# 병렬 실행
for i in "${!NODES[@]}"; do
  NODE="${NODES[$i]}"
  DIR="${DIRS[$i]}"

  echo "🚀 $NODE 노드에서 ORCA 실행 중: $DIR"
  ssh "$NODE" "cd $DIR && nohup $ORCA input.inp > input.out 2>&1 &" &
done

wait  # 모든 백그라운드 ssh 명령 종료까지 기다림 (필요 없으면 제거 가능)
echo "✅ 모든 노드에 명령 전송 완료!"


