# coding: utf-8
import os,sys,glob,re
import shutil

base=os.getcwd()
os.chdir(base)

# ===== set parameter below ====================
script_path = '/home/phzd/g09E/gmx'

# ====== end set parameter ======================

charge = 0
try:
	args = sys.argv[1:]
	print('args = ',args)
except:
	print('no args was found as charge, will use charge as 0')
	charge = 0
if len(args) > 0: charge = int(args[0])

rm_files_list = ['complex.gro', 'posre.itp', 'protein.gro', 'posre_ligand.itp', 'complex_box.gro', 'complex_SOL.gro', 'system.gro', 'em.trr', 'em.gro', 'mdout.mdp', 'em.log', 'em.edr', 'ligand_GMX.gro', 'ligand_GMX.itp', 'topol.top', 'em.tpr']
for f in rm_files_list: 
	if os.path.exists(f):	os.remove(f)

#rm_dirs_list = ['ligand.acpype',]  # no need to remove this fold. And it usually take serval min to do acpype.py job
#for fold in rm_dirs_list: 
#	if os.path.exists(fold):	shutil.rmtree(fold)
## os.removedirs can rm empty dir

if not os.path.exists('mpd'):
	bashline = 'cp -r {}/mdp ./ '.format(script_path)
	os.system(bashline)
	print('successful cp mdp fold into current fold')
if not os.path.exists('gmx_run_parameters'):
	bashline = 'cp -r {}/mdp/gmx_run_parameters ./ '.format(script_path)
	os.system(bashline)
	print('successful cp gmx_run_parameters file into current fold')
print('note: please modify gmx_run_parameters file, and mdp file in mdp fold and carefully examine the ligand.mol2 file using maestro or gview(gv)')

