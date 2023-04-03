from pathlib import Path
import os
import leitura as ler
import optimization as opt
import sys
from gurobipy import GRB
import numpy as np
from datetime import datetime, date

#######################################################################
###                    PARAMETROS                                  ###    
######################################################################

file_name = sys.argv[1]

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

def main():

#######################################################################
###                    LEITURA                                     ###    
######################################################################

	N, PP, PR, FP, FR, HR, HP, D, R, C = ler.leitura_instance(os.path.join(INSTANCE_PATH,file_name))

	xp_sol = [0]*N
	xr_sol = [0]*N
	sp_sol = [0]*N
	sr_sol = [0]*N
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

	obj,temp = opt.ulsr_sp_lp(N, PP, PR, FP, FR, HR, HP, D, R, SD, SR, C)
		
	arquivo = open(os.path.join(RESULT_PATH,'ulsr_sp_lp.txt'),'a')
	arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(temp,3))+'\n')
	arquivo.close()

if __name__== "__main__" :
	main()
