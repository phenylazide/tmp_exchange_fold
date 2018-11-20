# coding: utf-8
import os,sys,glob,re

base=os.getcwd()
os.chdir(base)
print("typical usage1: python 02_box_SOL_ions_MM.py\nypical usage2:python 02_box_SOL_ions_MM.py xx_tmp_fold\nypical usage3: python 02_box_SOL_ions_MM.py restrict_MM xx_tmp_fold")

# ===== set parameter below ====================
script_path = '/home/phzd/g09E/gmx'

# ====== end set parameter ======================

def check_determine_tmpfile():  ## using 'tmp{:0>2}'.format(), this is better, eliminating 
	"""
	os.chdir(base)
	tmp_list = ['tmp'+str(i) for i in range(100)]
	for f in tmp_list:
		if not os.path.exists(f):
			os.mkdir(f)
			print('new tmp fold: {} was just created'.format(f))
			return f
	raise Exception('error: tmp fold seems exceed 100, need del some')
	"""
	os.chdir(base)
	tmp_current_list = glob.glob('tmp*')
	if tmp_current_list == []: 		
		os.mkdir('tmp00')
		print('new tmp fold: {} was just created'.format('tmp00'))
		return 'tmp00'
	"""			
	tmp_max_fold = sorted(tmp_current_list)[-1]
	num = int(tmp_max_fold[3:])
	"""
	tmp_list_txt = ' '.join(tmp_current_list)
	pattern = re.compile("tmp(\d+)")
	match = re.findall(pattern, tmp_list_txt)
	num_list = [int(i) for i in match]	
	num = max(num_list)
	if num > 99: raise IOError('error: tmp fold seems exceed 100, need del some')
	new_tmp = 'tmp{:0>2}'.format(str(num+1))
	os.mkdir(new_tmp)
	print('new tmp fold: {} was just created'.format(new_tmp))	
	return new_tmp

def check_determine_tmpfile():  ## using 'tmp{:0>2}'.format(), this is better, eliminating 
	"""
	os.chdir(base)
	tmp_list = ['tmp'+str(i) for i in range(100)]
	for f in tmp_list:
		if not os.path.exists(f):
			os.mkdir(f)
			print('new tmp fold: {} was just created'.format(f))
			return f
	raise Exception('error: tmp fold seems exceed 100, need del some')
	"""
	os.chdir(base)
	tmp_current_list = glob.glob('tmp*')
	if tmp_current_list == []: 		
		os.mkdir('tmp00')
		print('new tmp fold: {} was just created'.format('tmp00'))
		return 'tmp00'
	"""			
	tmp_max_fold = sorted(tmp_current_list)[-1]
	num = int(tmp_max_fold[3:])
	"""
	tmp_list_txt = ' '.join(tmp_current_list)
	pattern = re.compile("tmp(\d+)")
	match = re.findall(pattern, tmp_list_txt)
	num_list = [int(i) for i in match]	
	num = max(num_list)
	if num > 99: raise IOError('error: tmp fold seems exceed 100, need del some')
	new_tmp = 'tmp{:0>2}'.format(str(num+1))
	os.mkdir(new_tmp)
	print('new tmp fold: {} was just created'.format(new_tmp))	
	return new_tmp

def read_restrict_MM_threads_from_parameters(xx_path):  
	"""
ligand_charge: 
restrict_MM_threads: 
em_mdp_file: 
gpu_OMP_NUM_THREADS: 4 
gpu_ntmpi: 4
	"""
	os.chdir(xx_path)
	print('read_restrict_MM_threads_from_parameters')
	f = open('gmx_run_parameters','r')
	txt = f.read()
	f.close()
	#pattern1 = re.compile('restrict_MM_threads: *(\d+)')
	pat1a = re.compile('gpu_OMP_NUM_THREADS: *(\d+)')
	pat1b = re.compile('gpu_ntmpi: *(\d+)')
	#pattern2 = re.compile('em_mdp_file: *([+-]*\d+)')
	pattern3 = re.compile('-conc *(\d+\.\d+)')
	#match1 = re.findall(pattern1,txt)
	mat1a = re.findall(pat1a,txt); mat1b = re.findall(pat1b,txt)
	match3 = re.findall(pattern3,txt)
	gpu_OMP_NUM_THREADS = mat1a[0]; gpu_ntmpi = mat1b[0]
	#match2 = 
	#if match1: restrict_MM_threads = int(match1[0])
	#else: 
		#print('no restrict_MM_threads was found in gmx_run_parameters file, will use 10 as default')
		#restrict_MM_threads = 10
	ion_conc = match3[0] if match3 else ""
	return gpu_OMP_NUM_THREADS, gpu_ntmpi, ion_conc

# ========= begin tmp_fold below =====================	
def deal_with_tmp_fold(xx_tmp_fold):
	print('checking tmp fold ...')	
	tmp_full_path = base + '/' + xx_tmp_fold
	os.chdir(base)
	#os.system('cp mdp/*.mdp {0}/ && cp complex.gro topol.top ligand_GMX.itp posre.itp posre_ligand.itp gmx_run_parameters {0}/'.format(tmp_full_path))
	os.system('cp mdp/*.mdp {0}/ && cp complex.gro topol.top ligand_GMX.itp posre*.itp topol_Protein*.itp gmx_run_parameters {0}/'.format(tmp_full_path))
	os.chdir(tmp_full_path)
	#for f in ['complex.gro', 'topol.top', 'ligand_GMX.itp', 'posre.itp', 'posre_ligand.itp']:
	for f in ['complex.gro', 'topol.top', 'ligand_GMX.itp', 'posre_ligand.itp']:
		if not os.path.exists(f):raise Exception('error: key necessary file: {} was not found in the new tmp fold: {}'.format(f,xx_tmp_fold))
	if len(glob.glob('posre.itp')) + len(glob.glob('posre_Protein*.itp')) ==0:raise Exception('error: key necessary file posre missing')
	return tmp_full_path

# ========= end tmp_fold below =====================	


# ========= begin box, solvate, .tpr, ions steps below =====================	
def box_solvate_tpr_ions(xx_tmp_full_path):
	os.chdir(xx_tmp_full_path)
	print('now processing box, solvate, .tpr, ions steps')

	os.system("source /opt/gmx2018.4/bin/GMXRC")
	## set box
	for f in ['complex.gro']:
		if not os.path.exists(f):raise Exception('error: no {} file was missing in box step'.format(f))
	os.system('/opt/gmx2018.4/bin/gmx editconf -f complex.gro -o complex_box.gro -d 1.0 -bt cubic')

	# solvate
	for f in ['complex_box.gro']:
		if not os.path.exists(f):raise Exception('error: no {} file was missing in solvate step'.format(f))
	os.system('/opt/gmx2018.4/bin/gmx solvate -cp complex_box.gro -o complex_SOL.gro -p topol.top')

	# Use grompp to assemble a .tpr file, using any .mdp file. such as em.mdp energy minimization, 
	for f in ['complex_SOL.gro']:
		if not os.path.exists(f):raise Exception('error: no {} file was missing in grompp to assemble a .tpr file step'.format(f))
	os.system('/opt/gmx2018.4/bin/gmx grompp -f em.mdp -c complex_SOL.gro -p topol.top -o em.tpr -maxwarn 5')

	## add ions: pass our .tpr file to genion: 
	ion_conc = read_restrict_MM_threads_from_parameters(xx_tmp_full_path)[2]
	conc_txt = '-conc {}'.format(ion_conc) if ion_conc != '' else ''
	if conc_txt: print('will use NaCl in {}'.format(conc_txt))
	for f in ['em.tpr']:
		if not os.path.exists(f):raise Exception('error: no {} file was missing in add ions step'.format(f))
	os.system("echo 'SOL' |/opt/gmx2018.4/bin/gmx genion -s em.tpr -p topol.top -o system.gro -neutral {}".format(conc_txt))  # -pname NA -nname CL;  0.15M NaCl, would be better in principle
	print('done with: tmp_fold, box, solvate, .tpr, ions steps')
	return
# ========= end tmp_fold, box, solvate, .tpr, ions steps  =====================	


# ========= begin minimization below =====================	
## minimization
def minimization(xx_tmp_full_path):
	print('now minimization ...')
	os.chdir(xx_tmp_full_path)
	for f in ['em.mdp','system.gro']:
		if not os.path.exists(f):raise Exception('error: no {} file was missing in add ions step'.format(f))
	os.system("/opt/gmx2018.4/bin/gmx grompp -f em.mdp -c system.gro -p topol.top -o em.tpr && export gpu_OMP_NUM_THREADS=2 && /opt/gmx2018.4/bin/gmx mdrun -v -deffnm em -gpu_ntmpi 4")
	## will generate 4 new files: em.log, em.gro, em.trr, em.edr
	for f in ['em.log', 'em.gro', 'em.trr', 'em.edr']:
		if not os.path.exists(f):raise Exception('error: minimization failed, no {} file was not generated after this minimization step'.format(f))
	return
# ========= end minimization ===========================	


# ========= begin restricted MM below =====================	
def restricted_MM(xx_tmp_full_path):
	print('now restricted MM ...')
	os.chdir(xx_tmp_full_path)
	for f in ['pr.mdp','em.gro','topol.top']:
		if not os.path.exists(f):raise Exception('error: no {} file as required was found in restricted MM step '.format(f))
	restrict_MM_threads = 10
	os.chdir(xx_tmp_full_path)
	if os.path.exists('gmx_run_parameters'):
		gpu_OMP_NUM_THREADS, gpu_ntmpi, ion_conc = read_restrict_MM_threads_from_parameters(xx_tmp_full_path)
	os.chdir(xx_tmp_full_path)
	bashline = '/opt/gmx2018.4/bin/gmx grompp -f pr.mdp -c em.gro -r em.gro  -p topol.top -o pr.tpr' # export gpu_OMP_NUM_THREADS=4; /opt/gmx2018.4/bin/gmx mdrun -v -deffnm pr 
	bashline1 = 'export gpu_OMP_NUM_THREADS={gpu_OMP_NUM_THREADS};/opt/gmx2018.4/bin/gmx mdrun -v -deffnm pr -gpu_ntmpi {gpu_ntmpi} -pin on -nb gpu'.format(gpu_OMP_NUM_THREADS=str(gpu_OMP_NUM_THREADS),gpu_ntmpi=str(gpu_ntmpi))
	os.system(bashline)
	os.system(bashline1)
	print('done with restict_MM, and the fold is :{}'.format(xx_tmp_full_path))
# ========= end restricted MM below =====================	

def main():
	try:
		args = sys.argv[1:]
		print('args = ',args)
	except:
		print('no args was found')
	tmp_fold = ''
	if len(args) == 0: # normal process
		tmp_fold = check_determine_tmpfile()
		tmp_full_path = deal_with_tmp_fold(tmp_fold)
		box_solvate_tpr_ions(tmp_full_path)
		minimization(tmp_full_path)
		restricted_MM(tmp_full_path)		
		return
	if len(args) > 0 and ('restrict' in args[0]) and ('MM' in args[0]):
		if len(args) == 1: raise Exception('error, to run restrict_MM only, please specify tmp_fold')
		if len(args) >= 1: 
			tmp_fold = args[1]
			tmp_full_path = '{}/{}'.format(base,tmp_fold)
			print('tmp_full_path is:{}, will use this do only estrict_MM step'.format(tmp_full_path))
			restricted_MM(tmp_full_path)
			return
	else:    ## specify tmp_fold, and do box_solvate_tpr_ions, minimization and restricted_MM
		tmp_fold = args[0]
		tmp_full_path = '{}/{}'.format(base,tmp_fold)
		box_solvate_tpr_ions(tmp_full_path)
		minimization(tmp_full_path)
		restricted_MM(tmp_full_path)
		return		
		
if __name__ == '__main__':
	main()


