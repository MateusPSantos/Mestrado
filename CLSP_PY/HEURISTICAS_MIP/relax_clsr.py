import gurobipy as gp
import leitura as ler
from gurobipy import GRB
from pathlib import Path
import os
import numpy as np
import sys
from datetime import datetime, date
import random as rd



def main():


   #######################################################################
	###                    PARAMETROS                                  ###    
	######################################################################

	
	cap = True
	file_name = sys.argv[1]

	MAX_CPU_TIME = 3600.0
	EPSILON = 0.000001

	
	INSTANCE_PATH = Path('../instances/sifaleras')
	RESULT_PATH   = Path('../RESULTADOS/')




	#######################################################################
	###                    LEITURA                                     ###    
	######################################################################




	N, PP, PR, FP, FR, HR, HP, D, R = ler.leitura_instance(file_name)


	SD = (np.zeros((N,N))).tolist()
	SR = (np.zeros((N,N))).tolist()
	for  i in range(N):
		SD[i][i] = D[i]
		SR[i][i] = R[i]
		for j in range(i+1, N):
			SD[i][j] = SD[i][j-1] + D[j]
			SR[i][j] = SR[i][j-1] + R[j]


			
	soma = sum(D)
	fator = 1.5
	#Capacidade de cada período
	C = (soma * fator)/N
	obj = 0

	#Guarda solução

	xp_sol = [0]*N
	xr_sol = [0]*N
	sp_sol = [0]*N
	sr_sol = [0]*N
	yp_sol = [0]*N
	yr_sol = [0]*N
	

	objval = 0
	bestbound = 0
	numnode = 0
	temp = 0
	gap = 0

	def timer(start_time=None):
		if not start_time:
			start_time = datetime.now()
			return start_time
		elif start_time:
			thour, temp_sec = divmod(
				(datetime.now() - start_time).total_seconds(), 3600)
			
			return temp_sec



	def gera_particoes(N,semente = 42,tamanho_particao=3,indice_geracao = 1):
		subset = []
        
		if indice_geracao == 1:
			for i in range(0,N,tamanho_particao):
				if i + tamanho_particao > N:
					subset.append([k for k in range(i,N)])
				else:
					subset.append([k for k in range(i,i+tamanho_particao)])
		else:
			from random import sample
			import random
			random.seed(semente)
			lista_periodos = [k  for k in range(N)]
			while True:
                
				sub_conj = []
                
				if len(lista_periodos) >= tamanho_particao:
					sub_conj = sample(lista_periodos,tamanho_particao)
				else:
					sub_conj = lista_periodos[:]
				subset.append(sub_conj)
				for i in sub_conj:
					lista_periodos.remove(i)
				if len(lista_periodos)==0:
					break
		return subset


	subset = gera_particoes(N)

	'''
	*********************************************************************
	***                    RELAX FIX                                  ***
	*********************************************************************
	'''

	def relax_fix(particoes,yp_sol ,yr_sol):
		try:

			# Create a new model
			model = gp.Model("CLSR")

			# Create variables
			
			xp = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="xp")
			yp = model.addVars(list(range(N)), lb =0.0, ub = 1.0,vtype=GRB.BINARY, name="yp")
			sp = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="sp")
			xr = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="xr")
			yr = model.addVars(list(range(N)), lb =0.0, ub = 1.0,vtype=GRB.BINARY, name="yr")
			sr = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="sr")
			
			for i in range(N):
				if i > max(particoes) :
					yp[i].VType = gp.GRB.CONTINUOUS
					yp[i].lb    = 0
					yp[i].ub    = 1
					yr[i].VType = gp.GRB.CONTINUOUS
					yr[i].lb    = 0
					yr[i].ub    = 1
				elif i in particoes:
					yp[i].lb = 0
					yp[i].ub = 1
					yr[i].lb = 0
					yr[i].ub = 1
				else:
					yp[i].lb = yp_sol[i]
					yp[i].ub = yp_sol[i]
					yr[i].lb = yr_sol[i]
					yr[i].ub = yr_sol[i]

			
			model.update()

			# # Set objective
			model.setObjective(gp.quicksum(PP[i]*xp[i]+sp[i]*HP[i] + xr[i]*PR[i] + sr[i]*HR[i] + yp[i]*FP[i] + yr[i]*FR[i] for i in range(N)) , sense = GRB.MINIMIZE)

			# # Add constraints
			
			model.addConstr(xp[0]+xr[0]-sp[0] == D[0])

			model.addConstrs(sp[i-1] + xp[i] + xr[i] - sp[i] == D[i] for i in range(N) if i > 0 )
			model.addConstr(R[0] - xr[0] - sr[0] == 0)
			model.addConstrs(sr[i-1] + R[i] - xr[i] - sr[i] == 0 for i in range(N) if i > 0)
			model.addConstrs(xp[i] - yp[i]*min(C,SD[i][N-1]) <= 0 for i in range(N))
			model.addConstrs(xr[i] - yr[i]*min(SR[0][i], SD[i][N-1]) <= 0 for i in range(N))
			model.addConstrs(xp[i] + xr[i] <= C for i in range(N))

			
			#model.write(file_name+".lp")

			# Parameters 
			model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
			model.setParam(GRB.Param.MIPGap, EPSILON)
			model.setParam(GRB.Param.Threads,3)
			model.setParam(GRB.Param.Cuts, 3)
			model.setParam(GRB.Param.Presolve,1)


			# Optimize model
			model.optimize()


			objval = model.ObjVal
			bestbound = model.ObjBound
			numnode = model.NodeCount
			#elapsed = model.Runtimẹ
			gap = model.MIPGap
			
			
			xp_sol = [xp[i].X for i in range(N)]
			xr_sol = [xr[i].X for i in range(N)]
			sp_sol = [sp[i].X for i in range(N)]
			sr_sol = [sr[i].X for i in range(N)]
			yp_sol = [yp[i].X for i in range(N)]
			yr_sol = [yr[i].X for i in range(N)]


			print('Obj: %g' % model.ObjVal)

		except gp.GurobiError as e:
			print('Error code ' + str(e.errno) + ': ' + str(e))

		except AttributeError:
			print('Encountered an attribute error')

		return model.ObjVal, xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol, bestbound, numnode, gap


	#######################################################################
	###                    Modelo CLSR                                 ###    
	######################################################################



	def clsr_std_relax(xp_sol,xr_sol,sp_sol,sr_sol,yp_sol ,yr_sol):

		#indices = []
	   

		#if len(particoes) == 1 :
		#    indices = particoes.copy()
		#else :
		#    for  i in range(len(particoes)):
		 #       for j in range(len(particoes[i])):
		  #          indices.append(j)
		try:

			# Create a new model
			model = gp.Model("CLSR")

			# Create variables
		
			xp = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="xp")
			yp = model.addVars(list(range(N)), lb =0.0, ub = 1.0,vtype=GRB.BINARY, name="yp")
			sp = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="sp")
			xr = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="xr")
			yr = model.addVars(list(range(N)), lb =0.0, ub = 1.0,vtype=GRB.BINARY, name="yr")
			sr = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="sr")

		  
			for i in range(N):
				xp[i].start = xp_sol[i]
				xr[i].start = xr_sol[i]
				sp[i].start = sp_sol[i]
				sr[i].start = sr_sol[i]
				yp[i].start = yp_sol[i]
				yr[i].start = yr_sol[i]
			
			model.update()
			# # Set objective
			model.setObjective(gp.quicksum(PP[i]*xp[i]+sp[i]*HP[i] + xr[i]*PR[i] + sr[i]*HR[i] + yp[i]*FP[i] + yr[i]*FR[i] for i in range(N)) , sense = GRB.MINIMIZE)

			# # Add constraints
		
			model.addConstr(xp[0]+xr[0]-sp[0] == D[0])

			model.addConstrs(sp[i-1] + xp[i] + xr[i] - sp[i] == D[i] for i in range(N) if i > 0 )
			model.addConstr(R[0] - xr[0] - sr[0] == 0)
			model.addConstrs(sr[i-1] + R[i] - xr[i] - sr[i] == 0 for i in range(N) if i > 0)
			model.addConstrs(xp[i] - yp[i]*min(C,SD[i][N-1]) <= 0 for i in range(N))
			model.addConstrs(xr[i] - yr[i]*min(SR[0][i], SD[i][N-1]) <= 0 for i in range(N))
			model.addConstrs(xp[i] + xr[i] <= C for i in range(N))
		   # model.write(file_name+"_model.lp")

			# Parameters 
			model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
			model.setParam(GRB.Param.MIPGap, EPSILON)
			model.setParam(GRB.Param.Threads,3)
			model.setParam(GRB.Param.Cuts, 3)
			model.setParam(GRB.Param.Presolve,2)



			# Optimize model
			model.optimize()

			xp_sol = [xp[i].X for i in range(N)]
			xr_sol = [xr[i].X for i in range(N)]
			sp_sol = [sp[i].X for i in range(N)]
			sr_sol = [sr[i].X for i in range(N)]
			yp_sol = [yp[i].X for i in range(N)]
			yr_sol = [yr[i].X for i in range(N)]




			print('Obj: %g' % model.ObjVal)

		except gp.GurobiError as e:
			print('Error code ' + str(e.errno) + ': ' + str(e))

		return model.ObjVal, xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol




	'''
    *********************************************************************
    ***                FIX AND OPTIMIZE                               ***
    *********************************************************************
    '''
	def fix_and_optimize(particoes,yp_sol ,yr_sol,num_subset):

		indices = []
        #indices = particoes.copy()

		if num_subset == 1 :
			indices = particoes.copy()
		else :
			for  i in range(len(particoes)):
				for j in range(len(particoes[i])):
					indices.append(j)
		try:

			# Create a new model
			model = gp.Model("CLSR")

			# Create variables
        
			xp = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="xp")
			yp = model.addVars(list(range(N)), lb =0.0, ub = 1.0,vtype=GRB.BINARY, name="yp")
			sp = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="sp")
			xr = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="xr")
			yr = model.addVars(list(range(N)), lb =0.0, ub = 1.0,vtype=GRB.BINARY, name="yr")
			sr = model.addVars(list(range(N)), lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="sr")

          
			for i in range(N):
				if i in indices:
					yp[i].lb    = 0
					yp[i].ub    = 1
					yr[i].lb    = 0
					yr[i].ub    = 1
				else:
					yp[i].lb    = yp_sol[i]
					yp[i].ub    = yp_sol[i]
					yr[i].lb    = yr_sol[i]
					yr[i].ub    = yr_sol[i]
            
			model.update()
			# # Set objective
			model.setObjective(gp.quicksum(PP[i]*xp[i]+sp[i]*HP[i] + xr[i]*PR[i] + sr[i]*HR[i] + yp[i]*FP[i] + yr[i]*FR[i] for i in range(N)) , sense = GRB.MINIMIZE)

			# # Add constraints
        
			model.addConstr(xp[0]+xr[0]-sp[0] == D[0])


			model.addConstrs(sp[i-1] + xp[i] + xr[i] - sp[i] == D[i] for i in range(N) if i > 0 )
			model.addConstr(R[0] - xr[0] - sr[0] == 0)
			model.addConstrs(sr[i-1] + R[i] - xr[i] - sr[i] == 0 for i in range(N) if i > 0)
			model.addConstrs(xp[i] - yp[i]*min(C,SD[i][N-1]) <= 0 for i in range(N))
			model.addConstrs(xr[i] - yr[i]*min(SR[0][i], SD[i][N-1]) <= 0 for i in range(N))
			model.addConstrs(xp[i] + xr[i] <= C for i in range(N))
           # model.write(file_name+"_model.lp")

            # Parameters 
			model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
			model.setParam(GRB.Param.MIPGap, EPSILON)
			model.setParam(GRB.Param.Threads,3)
			model.setParam(GRB.Param.Cuts, 3)
			model.setParam(GRB.Param.Presolve,1)



            # Optimize model
			model.optimize()

			xp_sol = [xp[i].X for i in range(N)]
			xr_sol = [xr[i].X for i in range(N)]
			sp_sol = [sp[i].X for i in range(N)]
			sr_sol = [sr[i].X for i in range(N)]
			yp_sol = [yp[i].X for i in range(N)]
			yr_sol = [yr[i].X for i in range(N)]




			print('Obj: %g' % model.ObjVal)
		
		except gp.GurobiError as e:
			print('Error code ' + str(e.errno) + ': ' + str(e))

		return model.ObjVal, xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol
    
	'''
	*********************************************************************
	***                LOCAL SEARCH HEURISTIC                         ***
	*********************************************************************
	'''
	def heuristic(subset,yp_sol,yr_sol):
      
	
		for particao in subset:
			obj,xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol,bestbound, numnode, gap = relax_fix(particao,yp_sol,yr_sol)
   

		for particao in subset:
			obj,xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol = fix_and_optimize(particao,yp_sol,yr_sol,1)
		
		obj_    = obj
		xp_sol_ = xp_sol.copy()
		xr_sol_ = xr_sol.copy()
		sp_sol_ = sp_sol.copy()
		sr_sol_ = sr_sol.copy()
		yp_sol_ = yp_sol.copy()
		yr_sol_ = yr_sol.copy()
        
		import random
		from random import sample
		random.seed(27)

		seed_random = sample(range(0,500),250) #[12,37,42,45,54,73,85,99]
		
		for semente in seed_random:
			
			subset = gera_particoes(N,semente=semente,tamanho_particao=2,indice_geracao=2)
			for particao in subset:
				obj_,xp_sol_,xr_sol_,sp_sol_,sr_sol_, yp_sol_,yr_sol_ = fix_and_optimize(particao,yp_sol_,yr_sol_,1)
			

			if  obj_ < obj :
				obj = obj_
				xp_sol = xp_sol_.copy()
				xr_sol = xr_sol_.copy()
				sr_sol = sr_sol_.copy()
				yp_sol = yp_sol_.copy()
				yr_sol = yr_sol_.copy()
    

		

		return obj,xp_sol,xr_sol, sp_sol,sr_sol, yp_sol,yr_sol

		


	'''
	*********************************************************************
	***                LOCAL SEARCH HEURISTIC                         ***
	*********************************************************************
	'''
 

	def	model_with_sol(subset,yp_sol,yr_sol):

		start	=	timer()
	
		obj,xp_sol,xr_sol,	sp_sol,sr_sol,	yp_sol,yr_sol	=	heuristic(subset,yp_sol,yr_sol)
			
		sol_fix_opt = obj


		obj,xp_sol,xr_sol,sp_sol,sr_sol,	yp_sol,yr_sol	=	clsr_std_relax(xp_sol,xr_sol,sp_sol,sr_sol,yp_sol,yr_sol)
		

		

		return obj,sol_fix_opt,xp_sol,xr_sol, sp_sol,sr_sol, yp_sol,yr_sol, timer(start)


	obj,sol_fix_opt,xp_sol,xr_sol, sp_sol,sr_sol, yp_sol,yr_sol,temp = model_with_sol(subset,yp_sol,yr_sol)

		
	arquivo = open('clsr_relax_table'+str(fator)+'.txt','a')
	arquivo.write(file_name+';'+str(round(sol_fix_opt,3))+';'+str(round(obj,3))+';'+str(temp)+'\n')
	arquivo.close()

if __name__== "__main__" :
	main()