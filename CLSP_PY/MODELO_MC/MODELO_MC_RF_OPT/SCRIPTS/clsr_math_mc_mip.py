
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
tam_particao = int(sys.argv[2]) # Tamanho das partições
num_fix = int(sys.argv[3]) # número de variáveis que serão fixadas 

USE_FOP = True# Se usa o fix and optimize


#######################################################################
###                    DIRETÓRIOS                                   ###    
#######################################################################



RESULT_PATH   = Path('../RESULTADOS/')
RESULT_IND_PATH = Path('../RESULTADOS_INDIVIDUAIS/')
INSTANCE_PATH = Path('../../../../instances/c1sifa')

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



	N, PP, PR, FP, FR, HR, HP, D, R, C = ler.leitura_instance(os.path.join(INSTANCE_PATH,file_name))

	xp_sol = [0]*N
	xr_sol = [0]*N
	wp_sol = (np.zeros((N,N))).tolist()
	wr_sol = (np.zeros((N,N))).tolist()
	vor_sol = (np.zeros((N,N))).tolist()
	yp_sol = [0]*N
	yr_sol = [0]*N
	rf_xp_sol = [0]*N
	rf_xr_sol = [0]*N
	rf_wp_sol = (np.zeros((N,N))).tolist()
	rf_wr_sol = (np.zeros((N,N))).tolist()
	rf_vor_sol = (np.zeros((N,N))).tolist()
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


			
	
	subset = gera.gera_particoes(N,tamanho_particao = tam_particao,num_par_fix= num_fix)

	start_rf = timer()
	for conj in subset:
		rf_obj,rf_xp_sol,rf_xr_sol,rf_wp_sol,rf_wr_sol,rf_vor_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed = rf.relax_fix(conj,rf_yp_sol,rf_yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C)

	temp_rf = timer(start_rf)

	rf_obj1,rf_xp_sol1,rf_xr_sol1,rf_wp_sol1,rf_wr_sol1,rf_vor_sol,rf_yp_sol1,rf_yr_sol1, rf_bestbound1, rf_numnode1,rf_gap1,rf_elapsed1 =rf_obj,rf_xp_sol,rf_xr_sol,rf_wp_sol,rf_wr_sol,rf_vor_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed 
	
	temp_opt = 0.0
	if USE_FOP == True:
		#subset = gera.gera_particoes(N,tamanho_particao=10,num_par_fix=2,indice_geracao=1)
		start_opt = timer()
		for conj in subset:
			rf_obj,rf_xp_sol,rf_xr_sol,rf_wp_sol,rf_wr_sol,rf_vor_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed = fop.fix_and_optimize(conj,rf_yp_sol,rf_yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,rf_xp_sol,rf_xr_sol,rf_wp_sol,rf_wr_sol,rf_vor_sol)

		temp_opt = timer(start_opt)


	temp_total = timer(start_rf)
	obj,bestbound,gap,temp,numnode,tmp = opt.clsr_mc(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,rf_xp_sol,rf_xr_sol,rf_yp_sol,rf_yr_sol,rf_wp_sol,rf_wr_sol,rf_vor_sol)
	


		
	
	if USE_FOP == True:
		arquivo = open(os.path.join(RESULT_PATH,'clsr_MC_relax_and_opt_table_mip.txt'),'a')
		arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(temp,3))+';'+str(round(rf_obj1,3))+';'+str(round(temp_rf,3))+';'+str(round(rf_obj,3))+';'+str(round(temp_opt,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(numnode,3))+';'+str(round(temp_total,3))+';'+str(tmp)+
					'\n')
		arquivo.close()
	else :
		arquivo = open(os.path.join(RESULT_PATH,'clsr_MC_relax_fix_table_mip.txt'),'a')
		arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(rf_obj1,3))+';'+str(round(temp_rf,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(temp,3))+';'+str(round(numnode,3))+';'+str(round(temp_total,3))+';'+str(tmp)+
					'\n')
		arquivo.close()



	#Sol_instance = pd.DataFrame()
	#Sol_instance['xp_sol'] = pd.Series(xp_sol)
	#Sol_instance['xr_sol'] = pd.Series(xr_sol)
	#Sol_instance['wp_sol'] = pd.Series(wp_sol)
	#Sol_instance['wr_sol'] = pd.Series(wr_sol)
	#Sol_instance['yp_sol'] = pd.Series(yp_sol)
	#Sol_instance['yr_sol'] = pd.Series(yr_sol)

	#Sol_instance.to_csv(os.path.join(RESULT_IND_PATH,'sol_mc_instance_'+file_name),sep=';',index=False)

if __name__== "__main__" :
	main()
