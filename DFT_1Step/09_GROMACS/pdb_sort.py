import numpy as np
import sys
import os

if len(sys.argv) < 4:
    print("사용법: python fix_pdb.py <input_pdb> <residue_name> <desired_names_comma_separated>")
    sys.exit(1)

input_file = sys.argv[1]
resname_new = sys.argv[2].ljust(3)[:3]
desired_names_str = sys.argv[3]
desired_names = [name.strip() for name in desired_names_str.split(',') if name.strip()]

basename = os.path.splitext(os.path.basename(input_file))[0]
output_file = f"{basename}_sorted.pdb"

skip_prefix = ("COMPND", "AUTHOR", "CONECT", "MASTER", "END")

with open(input_file, "r") as f:
    lines = [line for line in f if not line.startswith(skip_prefix)]

# 원자 파싱
atoms = []
for line in lines:
    if line.startswith(("ATOM", "HETATM")):
        atoms.append({
            'raw': line,
            'type': line[:6].strip(),
            'idx': int(line[6:11]),
            'name': line[12:16].strip(),
            'resn': line[17:20].strip(),
            'chain': line[21],
            'resid': int(line[22:26]),
            'x': float(line[30:38]),
            'y': float(line[38:46]),
            'z': float(line[46:54]),
            'element': line[76:78].strip() or line[12:14].strip()
        })

# UNL 처리
unl_atoms = [a for a in atoms if a['resn'] == 'UNL']
hoh_atoms = [a for a in atoms if a['resn'] == 'HOH']
for a in unl_atoms:
    a['resn'] = resname_new

# DFS로 UNL 연결 정렬
coords = np.array([[a['x'], a['y'], a['z']] for a in unl_atoms])
n = len(unl_atoms)
adj = [[] for _ in range(n)]
bond_cutoff = {
    ('H', 'H'): 1.0, ('H', 'C'): 1.2, ('H', 'N'): 1.2, ('H', 'O'): 1.2,
    ('C', 'C'): 1.8, ('C', 'N'): 1.8, ('C', 'O'): 1.8, ('N', 'O'): 1.6,
    ('N', 'N'): 1.8, ('O', 'O'): 1.6,
}
default_cutoff = 1.6

for i in range(n):
    for j in range(i + 1, n):
        dist = np.linalg.norm(coords[i] - coords[j])
        key = tuple(sorted([unl_atoms[i]['element'], unl_atoms[j]['element']]))
        if dist < bond_cutoff.get(key, default_cutoff):
            adj[i].append(j)
            adj[j].append(i)

visited = [False] * n
ordered_atoms = []

def dfs(v):
    visited[v] = True
    ordered_atoms.append(unl_atoms[v])
    neighbors = adj[v]
    H_first = sorted([u for u in neighbors if not visited[u] and unl_atoms[u]['element'] == 'H'],
                     key=lambda x: unl_atoms[x]['name'])
    rest = sorted([u for u in neighbors if not visited[u] and unl_atoms[u]['element'] != 'H'],
                  key=lambda x: unl_atoms[x]['element'])
    for u in H_first + rest:
        dfs(u)

start = next((i for i, a in enumerate(unl_atoms) if a['name'] == 'N'), 0)
dfs(start)

# 이름 재지정
for i, atom in enumerate(ordered_atoms):
    atom['name'] = desired_names[i] if i < len(desired_names) else atom['name']
    atom['type'] = "ATOM"

# HOH 처리 (OW, HW1, HW2 이름 할당)
hoh_O_atoms = [a for a in hoh_atoms if a['element'] == 'O']
hoh_H_atoms = [a for a in hoh_atoms if a['element'] == 'H']
assigned = set()

for o_atom in hoh_O_atoms:
    o_atom['name'] = "OW"
    o_coord = np.array([o_atom['x'], o_atom['y'], o_atom['z']])
    h_dists = []
    for h_atom in hoh_H_atoms:
        if h_atom['idx'] in assigned:
            continue
        h_coord = np.array([h_atom['x'], h_atom['y'], h_atom['z']])
        dist = np.linalg.norm(o_coord - h_coord)
        h_dists.append((dist, h_atom))
    h_dists.sort(key=lambda x: x[0])
    for i, (_, h_atom) in enumerate(h_dists[:2]):
        h_atom['resid'] = o_atom['resid']
        h_atom['chain'] = o_atom['chain']
        h_atom['name'] = f"HW{i+1}"
        assigned.add(h_atom['idx'])
# 1. UNL (BAL) 처리 및 인덱스 지정
final_atoms = []
for i, atom in enumerate(ordered_atoms):
    atom['idx'] = i + 1
    final_atoms.append(atom)

# 2. TER 라인 생성 (UNL 마지막 원자 인덱스 기준)
ter_idx = final_atoms[-1]['idx'] + 1
ter_line = f"TER   {ter_idx:5d}      {final_atoms[-1]['resn']:<3s} {final_atoms[-1]['chain']}{final_atoms[-1]['resid']:4d}\n"

# 3. HOH 인덱스 재설정 (TER 이후부터 시작)
hoh_sorted = sorted(hoh_O_atoms + hoh_H_atoms, key=lambda x: x['idx'])
for i, atom in enumerate(hoh_sorted):
    atom['idx'] = ter_idx + i + 1  # 밀기
def format_atom(atom):
    return (
        f"{atom['type']:<6s}{atom['idx']:>5d}  "
        f"{atom['name']:<4s}{atom['resn']:>3s} "
        f"{atom['chain']}{atom['resid']:4d}    "
        f"{atom['x']:8.3f}{atom['y']:8.3f}{atom['z']:8.3f}\n"
    )

# 4. 출력
with open(output_file, "w") as f:
    for atom in final_atoms:
        f.write(format_atom(atom))
    f.write(ter_line)  # TER는 중간에 위치
    for atom in hoh_sorted:
        f.write(format_atom(atom))

