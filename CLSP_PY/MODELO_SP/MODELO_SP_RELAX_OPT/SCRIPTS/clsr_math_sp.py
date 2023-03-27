
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

USE_FOP = False# Se usa o fix and optimize


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



	N, PP, PR, FP, FR, HR, HP, D, R ,C= ler.leitura_instance(os.path.join(INSTANCE_PATH,file_name))


	rf_zsp_sol = (np.zeros((N,N))).tolist()
	rf_zsr_sol = (np.zeros((N,N))).tolist()
	rf_zr_sol = (np.zeros((N,N))).tolist()
	rf_l_sol = [0]*N
	rf_yp_sol = [0]*N
	rf_yr_sol = [0]*N


	fo_zsp_sol = (np.zeros((N,N))).tolist()
	fo_zsr_sol = (np.zeros((N,N))).tolist()
	fo_zr_sol = (np.zeros((N,N))).tolist()
	fo_l_sol = [0]*N
	fo_yp_sol = [0]*N
	fo_yr_sol = [0]*N


	zsp_sol = (np.zeros((N,N))).tolist()
	zsr_sol = (np.zeros((N,N))).tolist()
	zr_sol = (np.zeros((N,N))).tolist()
	l_sol = [0]*N
	yp_sol = [0]*N
	yr_sol = [0]*N




	SD = (np.zeros((N,N))).tolist()
	SR = (np.zeros((N,N))).tolist()
	for  i in range(N):
		SD[i][i] = D[i]
		SR[i][i] = R[i]
		for j in range(i+1, N):
			SD[i][j] = SD[i][j-1] + D[j]
			SR[i][j] = SR[i][j-1] + R[j]


			

	
	subset = gera.gera_particoes(N)
	print(subset)
	print("***********************************************************")
	print("relax_fix")
	print("***********************************************************")

	start_rf = timer()
	for conj in subset:
		rf_obj,rf_zsp_sol,rf_zsr_sol,rf_zr_sol,rf_l_sol,rf_yp_sol,rf_yr_sol, rf_bestbound, rf_numnode,rf_gap,rf_elapsed = rf.relax_fix(conj,rf_yp_sol,rf_yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C)

	temp_rf = timer(start_rf)

	fo_zsp_sol,fo_zsr_sol,fo_zr_sol,fo_l_sol,fo_yp_sol,fo_yr_sol = rf_zsp_sol,rf_zsr_sol,rf_zr_sol,rf_l_sol,rf_yp_sol,rf_yr_sol

	temp_opt = 0.0
	if USE_FOP == True:
		print("***********************************************************")
		print("fix_and_optimize")
		print("***********************************************************")
		#subset = gera.gera_particoes(N,tamanho_particao=10,num_par_fix=2,indice_geracao=1)
		start_opt = timer()
		for conj in subset:
			fo_obj,fo_zsp_sol,fo_zsr_sol,fo_zr_sol,fo_l_sol,fo_yp_sol,fo_yr_sol, fo_bestbound, fo_numnode,fo_gap,fo_elapsed = fop.fix_and_optimize(conj,fo_yp_sol,fo_yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,fo_zsp_sol,fo_zsr_sol,fo_zr_sol,fo_l_sol)

		temp_opt = timer(start_opt)


	obj,bestbound,gap,temp,numnode,zsp_sol,zsr_sol,zr_sol,l_sol, yp_sol,yr_sol = opt.clsr_sp(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,fo_zsp_sol,fo_zsr_sol,fo_zr_sol,fo_l_sol,fo_yp_sol,fo_yr_sol)
	
	temp_total = timer(start_rf)


		
	
	if USE_FOP == True:
		arquivo = open(os.path.join(RESULT_PATH,'clsr_STD_relax_and_opt_table'+str(fator)+'.txt'),'a')
		arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(temp,3))+';'+str(round(rf_obj,3))+';'+str(round(temp_rf,3))+';'+str(round(fo_obj,3))+';'+str(round(temp_opt,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(numnode,3))+';'+str(round(temp_total,3))+
					'\n')
		arquivo.close()
	else :
		arquivo = open(os.path.join(RESULT_PATH,'clsr_STD_relax_fix_table'+str(fator)+'.txt'),'a')
		arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(rf_obj,3))+';'+str(round(temp_rf,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(temp,3))+';'+str(round(numnode,3))+';'+str(round(temp_total,3))+
					'\n')
		arquivo.close()




if __name__== "__main__" :
	main()