gmx pdb2gmx -f case_001_sorted.pdb -o processed.gro -p topol.top -ff oplsaa -water tip3p -ter
gmx editconf -f processed.gro -o newbox.gro -c -d 1.0 -bt cubic
gmx grompp -f em.mdp -c newbox.gro -p topol.top -o em.tpr -maxwarn 1
# gmx grompp -f em.mdp -c solvated.gro -p topol.top -o em.tpr -maxwarn 1
gmx mdrun -deffnm em
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 1
gmx mdrun -deffnm nvt
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr -maxwarn 1
gmx mdrun -deffnm npt -ntmpi 1
gmx grompp -f md.mdp -c npt.gro -r npt.gro -t npt.cpt -p topol.top -o md.tpr -maxwarn 2
gmx mdrun -deffnm md -v -ntmpi 2



