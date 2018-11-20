import os,sys	
	
	
bashline7 = '(echo 0) | /opt/gmx2018.4/bin/gmx trjconv -f md_run.xtc -s md_run.tpr -o md_run_pbc_whole_tmp.xtc -pbc whole -n index.ndx'
bashline8 = '(echo "1" "0") | /opt/gmx2018.4/bin/gmx trjconv -f md_run_pbc_whole_tmp.xtc -s md_run.tpr -o fixedmd_run.xtc -center -pbc mol -n index.ndx'
os.system(bashline7 + ' && ' + bashline8)
bashline7 = '(echo 0) | /opt/gmx2018.4/bin/gmx trjconv -f md_run.gro -s md_run.tpr -o md_run_pbc_whole_tmp.gro -pbc whole -n index.ndx'
bashline8 = '(echo "1" "0") | /opt/gmx2018.4/bin/gmx trjconv -f md_run_pbc_whole_tmp.gro -s md_run.tpr -o fixedmd_run.gro -center -pbc mol -n index.ndx'
os.system(bashline7 + ' && ' + bashline8)
os.remove('md_run_pbc_whole_tmp.xtc')
os.remove('md_run_pbc_whole_tmp.gro')
