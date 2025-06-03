import numpy as np
import sys
import os

if len(sys.argv) < 3:
    print("사용법: python fix_pdb.py <input_pdb> <residue_name>")
    sys.exit(1)

input_file = sys.argv[1]
resname_new = sys.argv[2].ljust(3)[:3]  # 최대 3자, 1~2자일 경우 공백 추가
# 입력 파일명에서 경로 제거 및 확장자 제거
basename = os.path.splitext(os.path.basename(input_file))[0]

# 새로운 출력 파일명 생성
output_file = f"{basename}_sorted.pdb"

skip_prefix = ("COMPND", "AUTHOR", "CONECT", "MASTER", "END")

with open(input_file, "r") as f:
    lines = [line for line in f if not line.startswith(skip_prefix)]

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

# UNL 변경
unl_atoms = [a for a in atoms if a['resn'] == 'UNL']
hoh_atoms = [a for a in atoms if a['resn'] == 'HOH']
for a in unl_atoms:
    a['resn'] = resname_new

# DFS 연결
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

desired_names = [
    "N", "H1", "H2", "H3", "CA", "HA1", "HA2",
    "CB", "HB1", "HB2", "C", "O1", "O2"
]
for i, atom in enumerate(ordered_atoms):
    atom['name'] = desired_names[i] if i < len(desired_names) else atom['name']
    atom['type'] = "ATOM"

# HOH chain 정리
hoh_by_resid = {}
for atom in hoh_atoms:
    resid = atom['resid']
    if resid not in hoh_by_resid:
        hoh_by_resid[resid] = {'O': None, 'H': []}
    if atom['element'] == 'O':
        hoh_by_resid[resid]['O'] = atom
    elif atom['element'] == 'H':
        hoh_by_resid[resid]['H'].append(atom)

for group in hoh_by_resid.values():
    if group['O']:
        for h in group['H']:
            h['chain'] = group['O']['chain']

# 병합 및 재정렬
final_atoms = ordered_atoms + sorted(hoh_atoms, key=lambda x: x['idx'])
for i, atom in enumerate(final_atoms):
    atom['idx'] = i + 1

# 출력
def format_atom(atom):
    return (
        f"{atom['type']:<6s}{atom['idx']:5d} {atom['name']:<4s}{atom['resn']:<3s} {atom['chain']}"
        f"{atom['resid']:4d}    {atom['x']:8.3f}{atom['y']:8.3f}{atom['z']:8.3f}\n"
    )

with open(output_file, "w") as f:
    for atom in final_atoms:
        f.write(format_atom(atom))

