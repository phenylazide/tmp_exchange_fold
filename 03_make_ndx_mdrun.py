# coding: utf-8
import os,sys,glob,re

print('usage1: python 03_make_ndx_mdrun [traj or fix]  # then follow instructions to make_ndx\nusage2: python 03_make_ndx_mdrun [xx_tmp_fold or currentfold] ## which will use xx_tmp_fold to run whole process, and no need to interupt to entry fold again')
print('if want to change reg MM time and threads or openmpi, then need to modify the file: gmx_run_parameters')

base=os.getcwd()
bashline = "source /opt/gmx2018.4/bin/GMXRC"
os.system(bashline)
os.chdir(base)

def read_reg_MM_steps_threads_from_parameters(xx_run_fold=base):  
	os.chdir(xx_run_fold)
	print('read_reg_MM_steps_threads_from_parameters')
	f = open('gmx_run_parameters','r')
	txt = f.read()
	f.close()
	pattern3 = re.compile('reg_MM_steps: *(\d+)')
	pattern4 = re.compile('reg_MM_threads: *(\d+)')  # 
	pattern5 = re.compile('OMP_NUM_THREADS: *(\d+)')  # 	
	match3 = re.findall(pattern3,txt)
	match4 = re.findall(pattern4,txt)
	match5 = re.findall(pattern5,txt)
	if match3: read_reg_MM_steps = int(match3[0])
	else: 
		print('no reg_MM_steps was not found in gmx_run_parameters file, will use 500000 steps as default')
		read_reg_MM_steps = 500000
	if match4: reg_MM_threads = int(match4[0])
	else: 
		print('no reg_MM_threads was not found in gmx_run_parameters file, will use 500000 steps as default')
		reg_MM_threads = 500000	
	defined_OMP_NUM_THREADS = False
	if match5:
		defined_OMP_NUM_THREADS = True; OMP_NUM_THREADS = str(int(match5[0]))
		os.environ['OMP_NUM_THREADS'] = OMP_NUM_THREADS
		print('OMP_NUM_THREADS was set to {} according to mx_run_parameters'.format(OMP_NUM_THREADS))
	return read_reg_MM_steps,reg_MM_threads, defined_OMP_NUM_THREADS

def make_ndx_and_md_run(xx_run_fold=base):
	os.chdir(xx_run_fold)
	### ============= begin check	MM step files  which was generated from last MM step ==============
	for f in ['em.log', 'em.gro', 'em.trr', 'em.edr']:
		if not os.path.exists(f):raise Exception('error: minimization failed, no {} file was not generated after this minimization step'.format(f))		
	## ===========  end check MM step files =============			
	## ========= begin make_ndx below =====================	
	print('now is: make ndx, the cmd is: gmx make_ndx -f pr.gro\n# choose by typing:\n1 | 13\n# rename by typing:\nname xx_new_num protein_lig\n!xx_new_num\nname xx_new_num2 envir\nq')
	xx = input("Using default setting:(echo '1 | 13'; echo 'name 24 protein_lig'; echo '!24'; echo 'name 25 envir';echo 'q') ? yes (or no)")
	if xx == 'yes' or xx == 'Yes' or xx == 'YES' or xx == '':
		bashline4 = "(echo '1 | 13'; echo 'name 24 protein_lig'; echo '!24'; echo 'name 25 envir';echo 'q') |/opt/gmx2018.4/bin/gmx make_ndx -f pr.gro"   ## automatic always wrong
	elif xx == 'no' or xx == 'No' or xx == 'NO':
		bashline4="/opt/gmx2018.4/bin/gmx make_ndx -f pr.gro"	
	else: bashline4 = "(echo '1 | 13'; echo 'name 24 protein_lig'; echo '!24'; echo 'name 25 envir';echo 'q') |/opt/gmx2018.4/bin/gmx make_ndx -f pr.gro"
	os.system(bashline4)
	## ========= end make_ndx =====================	
	## ========== begin modify steps in md_run.mdp file according gmx_run_parameters file
	print('about to run reg MM, first modify steps according gmx_run_parameters file, 500000 steps equals 1 ns')
	os.chdir(xx_run_fold)
	for f in ['md.mdp']:
		if not os.path.exists(f):raise Exception('error: no {} file as required was found in pre reg MM step '.format(f))
	with open('md.mdp','r') as f:
		old_md_mdp_lines = f.readlines()
	read_reg_MM_steps,reg_MM_threads,defined_OMP_NUM_THREADS = read_reg_MM_steps_threads_from_parameters(xx_run_fold)
	pattern = re.compile('nsteps *\= *\d+')
	for i,line in enumerate(old_md_mdp_lines):
		match = re.findall(pattern,line)
		if match: break
	reg_MM_steps_line_txt = 'nsteps     = {}\n'.format(str(read_reg_MM_steps))
	run_md_lines = old_md_mdp_lines[:i] + [reg_MM_steps_line_txt] +old_md_mdp_lines[i+1:]
	with open('md_run.mdp','w') as f:
		for line in run_md_lines:
			f.write(line)
		print('new md_run.mdp has been written')	

	for f in ['md_run.mdp']:
		if not os.path.exists(f):raise Exception('error: no {} file as required was found in reg MM step '.format(f))
	## === end modify steps in md_run.mdp file ===============
	
	## =============begin run md_run ===================
	bashline5="/opt/gmx2018.4/bin/gmx grompp -f md_run.mdp -c pr.gro -p topol.top -o md_run.tpr -n index.ndx -maxwarn 10"
	os.system(bashline5)
	##raw_input = ('just pause after md_run.tpr,next will run reg MM')
	
	os.chdir(xx_run_fold)
	print('now running reg MM, threads is set to: {}'.format(str(reg_MM_threads)))
	bashline6 = '/opt/gmx2018.4/bin/gmx mdrun -v -deffnm md_run -nt {} -pin on'.format(str(reg_MM_threads))
	os.system(bashline6)
	print('md_run was done, hehe')
	print('the fold is: {}'.format(xx_run_fold))
	## ============= end run md_run ===================		
	return

def fixedmd_run_pbc_mol(xx_run_fold):
	os.chdir(xx_run_fold)
	for f in ['md_run.xtc','md_run.tpr']:
		if not os.path.exists(f):raise Exception('error: no {} file was found for correct trjconv'.format(f))
	#bashline7 = '(echo 0) | /opt/gmx2018.4/bin/gmx trjconv -f md_run.xtc -s md_run.tpr -o fixedmd_run.xtc -pbc mol'
	#os.system(bashline7)
	#bashline8 = '(echo 0) | /opt/gmx2018.4/bin/gmx trjconv -f md_run.gro -s md_run.tpr -o fixedmd_run.gro -pbc mol'
# echo "0"      | gmx trjconv -s md_0_1.tpr -f md_0_1.xtc -o md_0_1_whole.xtc -pbc whole -n index.ndx 
# echo "1 0"   | gmx trjconv -s md_0_1.tpr -f md_0_1_whole.xtc -o md_0_1_mol_center.xtc -center -pbc mol -n index.ndx
	bashline7 = '(echo 0) | /opt/gmx2018.4/bin/gmx trjconv -f md_run.xtc -s md_run.tpr -o md_run_pbc_whole_tmp.xtc -pbc whole -n index.ndx'
	bashline8 = '(echo "1" "0") | /opt/gmx2018.4/bin/gmx trjconv -f md_run_pbc_whole_tmp.xtc -s md_run.tpr -o fixedmd_run.xtc -center -pbc mol -n index.ndx'
	os.system(bashline7 + ' && ' + bashline8)
	bashline7 = '(echo 0) | /opt/gmx2018.4/bin/gmx trjconv -f md_run.gro -s md_run.tpr -o md_run_pbc_whole_tmp.gro -pbc whole -n index.ndx'
	bashline8 = '(echo "1" "0") | /opt/gmx2018.4/bin/gmx trjconv -f md_run_pbc_whole_tmp.gro -s md_run.tpr -o fixedmd_run.gro -center -pbc mol -n index.ndx'
	os.system(bashline7 + ' && ' + bashline8)
	os.remove('md_run_pbc_whole_tmp.xtc')
	os.remove('md_run_pbc_whole_tmp.gro')
	for f in ['fixedmd_run.xtc','fixedmd_run.gro']:
		if not os.path.exists(f):raise Exception('error: no {} file was found after trjconv step'.format(f))
	print('fixedmd_run.xtc and fixedmd_run.gro are ready with pbc whole center mol handling, whole process has beeen done')
	print('the fold is: {}'.format(xx_run_fold))

#===================
def interupt_for_input_tmp_fold():  ## no need to entry fold control here
	if sys.version_info.major==2:	input_fold = raw_input('please input the tmp fold name for run reg MM:')
	else:input_fold = input('please input the tmp fold name for run reg MM:')
	if input_fold == '' or input_fold == ' ': tmp_base = base;print('warning !!!!! will use current fold(not tem fold to run md_run')
	else:tmp_base = base + '/' + input_fold	
	return tmp_base

def main():
	try:
		args = sys.argv[1:]
		print('args,sys.argv[1:]=',args,sys.argv[1:])
	except:
		print('no args was found, will do the whole md_run and fix traj')

	if (len(args) == 1) and ('fix' in args[0] or 'traj' in args[0]):   ## if this directly return, simple
		fixedmd_run_pbc_mol(base)
		return
	if (len(args) == 0):		
		tmp_base = interupt_for_input_tmp_fold()
	elif len(args) == 1 and 'tmp' in args[0]:
		tmp_base = '{}/{}'.format(base,args[0])
	elif len(args) == 1 and ('currentfold' == args[0] or 'current' == args[0] or './' == args[0]):tmp_base = base
	else: raise IOError("tmp_base was not defined")
	print('tmp_base is {}, which is the main fold for run gmx md_run'.format(tmp_base))
	make_ndx_and_md_run(tmp_base)
	fixedmd_run_pbc_mol(tmp_base)

if __name__ == '__main__':
	main()			

