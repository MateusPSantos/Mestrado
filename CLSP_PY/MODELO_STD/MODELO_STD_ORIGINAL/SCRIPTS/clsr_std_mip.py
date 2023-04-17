
from pathlib import Path
import os
import leitura as ler
import optimization as opt
import numpy as np
import pandas as pd
import sys
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

	obj,bestbound,gap,temp,numnode,tmp,xp_sol,xr_sol,sp_sol,sr_sol,yp_sol,yr_sol = opt.clsr_std_mip(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C)
	
	arquivo = open(os.path.join(RESULT_PATH,'clsr_std_mip.txt'),'a')
	arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(bestbound,3))+\
					';'+str(round(gap,3))+';'+str(round(temp,3))+';'+str(round(numnode,3))+\
					';'+str(round(tmp,3))+
					'\n')

	arquivo.close()

	Sol_instance = pd.DataFrame()
	Sol_instance['xp_sol'] = pd.Series(xp_sol)
	Sol_instance['xr_sol'] = pd.Series(xr_sol)
	Sol_instance['sp_sol'] = pd.Series(sp_sol)
	Sol_instance['sr_sol'] = pd.Series(sr_sol)
	Sol_instance['yp_sol'] = pd.Series(yp_sol)
	Sol_instance['yr_sol'] = pd.Series(yr_sol)

	Sol_instance.to_csv(os.path.join(RESULT_IND_PATH,'sol_instance_'+file_name),sep=';',index=False)

if __name__== "__main__" :
	main()
