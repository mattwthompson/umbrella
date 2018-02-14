import os
import time

import numpy as np


PBS_HEADER = """#!/bin/sh -l
#PBS -l nodes=1:ppn=16
#PBS -l walltime=96:00:00
#PBS -q low
#PBS -N umbrella_{0}
#PBS -j oe
#PBS -V
#PBS -M myemail@server.me
#PBS -m abe


cd $PBS_O_WORKDIR

module load gromacs/5.1.4


"""

states_to_run = [int(val) for val in np.loadtxt('out.txt')[:, 0]]

chunk_size = int(len(states_to_run) / 4)

for chunk in np.array_split(states_to_run, chunk_size):
    PBS_FILE = PBS_HEADER.format('_'.join([str(state) for state in chunk]))
    for num in chunk:
        if not os.path.isfile('equil{0}.gro'.format(num)):
            equil_grompp_str = 'gmx grompp -f equil.mdp -c conf{0}.gro -p system.top -n pull_index.ndx -o equil{0}.tpr\n'.format(num)
            equil_mdrun_str = 'gmx mdrun -deffnm equil{0} -v -nt 16\n'.format(num)
            PBS_FILE += equil_grompp_str
            PBS_FILE += equil_mdrun_str

        if not os.path.isfile('umbrella{0}.gro'.format(num)):
            umbrella_grompp_str = 'gmx grompp -f md_umbrella.mdp -c equil{0}.gro -p system.top -n pull_index.ndx -o umbrella{0}.tpr\n'.format(num)
            if os.path.isfile('umbrella{0}.cpt'.format(num)):
                umbrella_mdrun_str = 'gmx mdrun -deffnm umbrella{0} -cpi umbrella{0}.cpt -pf pullf_umbrella{0}.xvg -px pullx_umbrella{0}.xvg -v -nt 16\n'.format(num)
            else:
                umbrella_mdrun_str = 'gmx mdrun -deffnm umbrella{0} -pf pullf_umbrella{0}.xvg -px pullx_umbrella{0}.xvg -v -nt 16\n'.format(num)
            PBS_FILE += umbrella_grompp_str
            PBS_FILE += umbrella_mdrun_str

    if not (os.path.isfile('equil{0}.gro'.format(num)) and os.path.isfile('umbrella{0}.gro'.format(num))):
        outfile = 'umbrella_{0}.pbs'.format('_'.join([str(state) for state in chunk]))

        with open(outfile, 'w') as fo:
            fo.write(PBS_FILE)
        time.sleep(0.1)  # Sleep for 100 ms to preserve order of written files
