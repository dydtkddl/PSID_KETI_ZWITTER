#!/bin/bash

# 사용법: ./generate_density.sh input.gbw
# input.gbw 파일명을 인자로 넘기세요

if [ $# -ne 1 ]; then
  echo "Usage: $0 input.gbw"
  exit 1
fi

GBW_FILE=$1
BASENAME=${GBW_FILE%.gbw}

echo "Processing $GBW_FILE ..."

orca_plot "$GBW_FILE" -i << EOF
1
2
y
4
120
5
7
11
12
EOF

echo "Density plot completed for $GBW_FILE"

