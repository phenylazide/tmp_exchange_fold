# coding: utf-8
import os,sys,glob,re

## cp three files;  
## edit complex.gro twice(num of atom, cp ligand_GMX.gro coordinate)
## (echo 0)| gmx genrestr -f ligand_GMX.gro -o posre_ligand.itp
## edit ligand_GMX.itp, add 

#ifdef POSRES
#include "posre_ligand.itp"
#endif

base=os.getcwd()
os.chdir(base)
ff_dict = {'amber03':'1','amber99':'6','amber14':'10', 'charmm36':'9'}   

# ===== set parameter below ====================
script_path = '/home/phzd/g09E/gmx'
# /opt/gmx2018.4/bin/gmx
# ====== end set parameter ======================
print('usage: python 01_build_cmplx_top_itp  ## before that just prepare protein.pdb and ligand.mol2')
print('the script will cp mdp files and acpype.py')

"""
def read_charge_and_ff_from_gmx_run_parameters():  	
	os.chdir(base)
	print('now read_charge_and_ff_from_gmx_run_parameters')
	f = open('gmx_run_parameters','r')
	txt = f.read()
	f.close()
	pattern = re.compile('ligand_charge: *([+-]*\d+)')
	pattern1 = re.compile('forece_field: *(\w+)')
	match = re.findall(pattern,txt)
	match1 = re.findall(pattern1,txt)	
	read_charge = int(match[0]) if match else ''
	read_ff = match1[0] if match1 else ''
	input_charge = input('please input the ligand charge: ')
	print('read_charge, input_charge = ', read_charge, input_charge)
	if input_charge != '' and input_charge != ' ' and input_charge != '\n':
		charge = int(input_charge);print('input charge is: {} which will be adopted'.format(input_charge)) 	
	elif read_charge != '': charge = read_charge
	else: charge = 0; print('no charge was defined by input or gmx_run_parameters file, will use charge = 0')
	
	input_ff = input('please input the applying forecefied: ')
	print('read_ff,input_ff= ', read_ff,input_ff)
	if input_ff != '' and input_ff != ' ' and input_ff != '\n':
		applying_ff = input_ff;print('applying_ff is: {} which will be adopted'.format(applying_ff)) 
	elif read_ff != '': applying_ff = read_ff
	else: applying_ff = 'abmer03'; print('no forcefield was defined by input or gmx_run_parameters file, will use abmer03')
	return charge,applying_ff
	
read_charge,applying_ff = read_charge_and_ff_from_gmx_run_parameters()

try:
	args = sys.argv[1:]
	print('args = ',args)
except:
	print('no args was found as charge, will use charge as 0')
	charge = 0
if len(args) == 0: 
	charge = read_charge
	print('no args was found as charge, will use read_charge which is: {}'.format(str(read_charge)))
if len(args) > 0: 
	charge = int(args[0])
	print('charge is set to {} by sys.args'.format(args[0]))
"""
################
def read_charge_and_ff_from_gmx_run_parameters():  
	"""
ligand_charge: 0
restrict_MM_threads: 32
reg_MM_steps: 500000   # nsteps     = 500000 ;this mean 1 ns
reg_MM_threads: 54
OMP_NUM_THREADS: 1
forece_field: amber03
	"""
	os.chdir(base)
	print('now read_charge_and_ff_from_gmx_run_parameters')
	input_charge_remind = input('reminder: please open gmx_run_parameters: \n1. change the correct ligand charge.\n2. choose the applying forecefied ')
	f = open('gmx_run_parameters','r')
	txt = f.read()
	f.close()
	pattern = re.compile('ligand_charge: *([+-]?\d+)')
	pattern1 = re.compile('forece_field: *(\w+)')
	match = re.findall(pattern,txt)
	match1 = re.findall(pattern1,txt)	
	read_charge = int(match[0]) if match else 0
	read_ff = match1[0] if match1 else 'charmm36'
	print('read_charge, read_ff = ', read_charge, read_ff)
	return read_charge,read_ff


try:
	args = sys.argv[1:]
	print('args = ',args)
except:
	print('no args was found, will use gmx_run_parameters')
	
read_charge,read_ff = read_charge_and_ff_from_gmx_run_parameters()

charge = read_charge if read_charge else 0
applying_ff = read_ff if read_ff else 'charmm36'
	

os.system('sed -i s/\ Ar/\ ar/g ligand.mol2')  ## need charge Ar to ar, as required by acpype.py and amber
if (not os.path.exists('ligand.acpype/ligand_GMX.gro')) or (not os.path.exists('ligand.acpype/ligand_GMX.itp')):
	bashline0 = 'source /home/phzd/test/amber16/amber.sh && python {}/acpype.py -i ligand.mol2 -n {}'.format(script_path, str(charge))
	os.system(bashline0)

for f in ['ligand.acpype/ligand_GMX.gro', 'ligand.acpype/ligand_GMX.itp']:
	if not os.path.exists(f):raise Exception('error: no {} file was generate'.format(f))

# ========= begin pdb2gmx, cp, genrestr below =====================
os.system("source /opt/gmx2018.4/bin/GMXRC")

bashline1 = '/opt/gmx2018.4/bin/gmx pdb2gmx -f protein.pdb -o protein.gro -p topol.top -ignh <<EOF\n{}\n1\nEOF\n'.format(ff_dict[applying_ff])     ### this is forcefield choosing step
os.system(bashline1)  ## use EOF instead of echo 

for f in ['protein.gro','topol.top']:
	if not os.path.exists(f):raise Exception('error: no {} file was generate'.format(f))

bashline2 = 'cp ligand.acpype/ligand_GMX.gro ./ && cp ligand.acpype/ligand_GMX.itp ./ && cp protein.gro complex.gro'.format(script_path)
os.system(bashline2)

## cp -r {}/mdp ./ &&  was put on 00_remove_failed_build_file.py

for f in ['ligand_GMX.gro','ligand_GMX.itp','complex.gro']:
	if not os.path.exists(f):raise Exception('error: no {} file was generate'.format(f))

bashline3 = "echo '0'| /opt/gmx2018.4/bin/gmx genrestr -f ligand_GMX.gro -o posre_ligand.itp"
os.system(bashline3)
for f in ['posre_ligand.itp']:
	if not os.path.exists(f):raise Exception('error: no {} file was generate'.format(f))

## ======== end pdb2gmx, cp, genrestr  =====================


### ==== modify complex.gro file below ====================
with open('complex.gro','r') as f:
	complex_gro_lines = f.readlines()

with open('ligand_GMX.gro','r') as f:
	ligand_GMX_gro_lines = f.readlines()

total_atom_num = int(complex_gro_lines[1]) + int(ligand_GMX_gro_lines[1])
total_atom_num_l = ' ' + str(total_atom_num) + '\n'
new_complex_gro_lines = [complex_gro_lines[0]] + [total_atom_num_l] + complex_gro_lines[2:-1] + ligand_GMX_gro_lines[2:-1] + [complex_gro_lines[-1]]

modify_complex_gro = False
with open('complex.gro','w') as f:
	for line in new_complex_gro_lines:
		f.write(line)
	modify_complex_gro = True
if not modify_complex_gro: raise Exception('error: failed in modify complex.gro file')
### ==== end modify complex.gro file ====================


### ==== modify ligand_GMX.itp below ====================
modify_ligand_GMX_itp = False
with open('ligand_GMX.itp','a') as f:
	append_txt = '#ifdef POSRES\n#include "posre_ligand.itp"\n#endif\n'
	f.write(append_txt)
	modify_ligand_GMX_itp = True	
if not modify_ligand_GMX_itp: raise Exception('error: failed in modify complex.gro file')
### ==== end modify ligand_GMX.itp ====================


### ==== modify topol.top file below ====================
with open('topol.top','r') as f:
	topol_lines = f.readlines()
	
append_lig_force_lines = ['\n', '; Include ligand topology\n', '#include "ligand_GMX.itp"\n', '\n', '\n']

append_lig_molecule_line = ['ligand              1\n']

pattern = re.compile('; *Include forcefield parameters')
for i,line in enumerate(topol_lines):
	match = re.findall(pattern,line)
	if match: break
	
new_topol_lines = topol_lines[:i+3] + append_lig_force_lines + topol_lines[i+3:] + append_lig_molecule_line

modify_topol = False
with open('topol.top','w') as f:
	for line in new_topol_lines:
		f.write(line)
	modify_topol = True
if not modify_topol: raise Exception('error: failed in modify topol file')
### ==== end modify topol.top file ====================




