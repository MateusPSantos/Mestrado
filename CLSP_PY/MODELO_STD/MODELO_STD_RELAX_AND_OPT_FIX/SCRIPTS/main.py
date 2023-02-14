
from pathlib import Path
import os
import leitura as ler
import optimization as opt
import relax_fix as rf
import fix_optimize as fop
import gera_particoes as gera
import numpy as np
import pandas as pd
import sys
from datetime import datetime, date


#######################################################################
###                    PARAMETROS                                  ###    
######################################################################



file_name = sys.argv[1]
fator = float(sys.argv[2])
USE_FOP = True# Se usa o fix and optimize


#######################################################################
###                    DIRETÓRIOS                                   ###    
#######################################################################



RESULT_PATH   = Path('../RESULTADOS/')
RESULT_IND_PATH = Path('../RESULTADOS_INDIVIDUAIS/')
INSTANCE_PATH = Path('../instances/sifaleras')

#######################################################################
###                    VARIÁVEIS GLOBAIS                           ###    
######################################################################


#Guarda solução



objval = 0
bestbound = 0
numnode = 0
temp = 0
gap = 0
obj = 0

from datetime import *
def timer(start_time=None):
	if not start_time:
		start_time = datetime.now()
		return start_time
	elif start_time:
		temp_sec = (datetime.now() - start_time).total_seconds()
		return temp_sec


def main():

#######################################################################
###                    LEITURA                                     ###    
######################################################################



	N, PP, PR, FP, FR, HR, HP, D, R = ler.leitura_instance(os.path.join(INSTANCE_PATH,file_name))

	xp_sol = [0]*N
	xr_sol = [0]*N
	sp_sol = [0]*N
	sr_sol = [0]*N
	yp_sol = [0]*N
	yr_sol = [0]*N
	rf_xp_sol = [0]*N
	rf_xr_sol = [0]*N
	rf_sp_sol = [0]*N
	rf_sr_sol = [0]*N
	rf_yp_sol = [0]*N
	rf_yr_sol = [0]*N
	rf_yp_sol = [0]*N
	rf_yr_sol = [0]*N




	SD = (np.zeros((N,N))).tolist()
	SR = (np.zeros((N,N))).tolist()
	for  i in range(N):
		SD[i][i] = D[i]
		SR[i][i] = R[i]
		for j in range(i+1, N):
			SD[i][j] = SD[i][j-1] + D[j]
			SR[i][j] = SR[i][j-1] + R[j]


			
	soma = sum(D)
	
	#Capacidade de cada período
	C = (soma * fator)/N
	
	subset = gera.gera_particoes(N)
	print(subset)
	print("***********************************************************")
	print("relax_fix")
	print("***********************************************************")

	start_rf = timer()
	for conj in subset:
		rf_obj,rf_xp_sol,rf_xr_sol,rf_sp_sol,rf_sr_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed = rf.relax_fix(conj,rf_yp_sol,rf_yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C)

	temp_rf = timer(start_rf)

	rf_obj1,rf_xp_sol1,rf_xr_sol1,rf_sp_sol1,rf_sr_sol1,rf_yp_sol1,rf_yr_sol1, rf_bestbound1, rf_numnode1,rf_gap1,rf_elapsed1 =rf_obj,rf_xp_sol,rf_xr_sol,rf_sp_sol,rf_sr_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed 
	
	temp_opt = 0.0
	if USE_FOP == True:
		print("***********************************************************")
		print("fix_and_optimize")
		print("***********************************************************")
		start_opt = timer()
		for conj in subset:
			rf_obj,rf_xp_sol,rf_xr_sol,rf_sp_sol,rf_sr_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed = fop.fix_and_optimize(conj,rf_yp_sol,rf_yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,rf_xp_sol,rf_xr_sol,rf_sp_sol,rf_sr_sol)

		temp_opt = timer(start_opt)


	obj,bestbound,gap,temp,numnode,xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol = opt.clsr_std(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,rf_xp_sol,rf_xr_sol,rf_sp_sol,rf_sr_sol,rf_yp_sol,rf_yr_sol)
	
	temp_total = timer(start_rf)


		
	
	if USE_FOP == True:
		arquivo = open(os.path.join(RESULT_PATH,'clsr_STD_relax_and_opt_table'+str(fator)+'.txt'),'a')
		arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(temp,3))+';'+str(round(rf_obj1,3))+';'+str(round(temp_rf,3))+';'+str(round(rf_obj,3))+';'+str(round(temp_opt,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(numnode,3))+';'+str(round(temp_total,3))+
					'\n')
		arquivo.close()
	else :
		arquivo = open(os.path.join(RESULT_PATH,'clsr_STD_relax_fix_table'+str(fator)+'.txt'),'a')
		arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(rf_obj1,3))+';'+str(round(temp_rf,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(temp,3))+';'+str(round(numnode,3))+';'+str(round(temp_total,3))+
					'\n')
		arquivo.close()



	Sol_instance = pd.DataFrame()
	Sol_instance['xp_sol'] = pd.Series(xp_sol)
	Sol_instance['xr_sol'] = pd.Series(xr_sol)
	Sol_instance['sp_sol'] = pd.Series(sp_sol)
	Sol_instance['sr_sol'] = pd.Series(sr_sol)
	Sol_instance['yp_sol'] = pd.Series(yp_sol)
	Sol_instance['yr_sol'] = pd.Series(yr_sol)

	Sol_instance.to_csv(os.path.join(RESULT_IND_PATH,'sol_instance_'+str(fator)+'_'+file_name),sep=';',index=False)

if __name__== "__main__" :
	main()