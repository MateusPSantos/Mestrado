
import gurobipy as gp
from gurobipy import GRB
import numpy as np

#######################################################################
###                    PARAMETROS                                  ###    
######################################################################



MAX_CPU_TIME = 600.0
EPSILON = 0.000001
cap = True





#######################################################################
###                    MODELO			                           ###    
######################################################################


def clsr_sp(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,zsp_sol,zsr_sol,zr_sol,l_sol,yp_sol,yr_sol):


	CSP = (np.zeros((N,N))).tolist()
	CSR = (np.zeros((N,N))).tolist()
	CR = (np.zeros((N,N))).tolist()
	CL = [0]*N

	for i in range(N):
		for j in range(i,N):
			CR[i][j]  = sum(HR[t]*SR[i][t] for t in range(i,j))
			CSP[i][j] = PP[i] * SD[i][j] + sum(HP[t]*SD[t+1][j] for t in range(i,j))
			CSR[i][j] = PR[i] * SD[i][j] + sum(HP[t]*SD[t+1][j] for t in range(i,j))

	for i in range(N):
		CL[i] = sum(HR[j]*SR[i][j] for j in range(i,N))
	


	try:

		# Create a new model
		model = gp.Model("CLSR")

		# Create variables
		
		zsp = model.addVars([(i,j) for i in range(N) for j in range(i,N)], lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="z_sp")
		zsr = model.addVars([(i,j) for i in range(N) for j in range(i,N)], lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="z_sr")
		zr  = model.addVars([(i,j) for i in range(N) for j in range(i,N)],lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="z_r")
		l    = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.CONTINUOUS, name="l")
		yp   = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.BINARY, name="yp")
		yr   = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.BINARY, name="yr")



		for i in range(N):
			l[i].start = l_sol[i]
			yp[i].start = yp_sol[i]
			yr[i].start = yr_sol[i]
			for j in range(i,N):
				zsp[i,j].start = zsp_sol[i][j]
				zsr[i,j].start = zsr_sol[i][j]
				zr[i,j].start = zr_sol[i][j]


		# # Set objective
		#FO = None
		#for i in range(N):
		#	FO += yp[i]*FP[i] + yr[i]*FR[i] + l[i]*CL[i] + gp.quicksum(zsp[i,j]*CSP[i][j] + zsr[i,j]*CSR[i][j]+
		#															   zr[i,j]*CR[i][j] for j in range(i,N))

		
		#model.setObjective(FO, sense = GRB.MINIMIZE)

		# # Add constraints

		# # Set objective
		FO = None
		for i in range(N):
			FO += yp[i]*FP[i] + yr[i]*FR[i] + l[i]*CL[i] 
			
			for j in range(i,N):
				FO+=zsp[i,j]*CSP[i][j] + zsr[i,j]*CSR[i][j]+zr[i,j]*CR[i][j] 

		model.setObjective(FO, sense = GRB.MINIMIZE)

		# # Add constraints

		model.addConstr(gp.quicksum(zsp[0,j]+zsr[0,j] for j in range(N)) ==1)

		
		model.addConstrs(gp.quicksum(zsp[i,t-1] + zsr[i,t-1] for i in range(t)) - gp.quicksum(zsp[t,j] + zsr[t,j] for j in range(t, N)) == 0  for t in range(1,N) )
		
		
		model.addConstrs(gp.quicksum(zsp[t,j] for j in range(t,N) if SD[t][j] > 0.0 ) <= yp[t] for t in range(N))
			
		
		
		model.addConstrs(gp.quicksum(zsr[t,j] for j in range(t,N) if SD[t][j] > 0.0) <= yr[t] for t in range(N))
			
			
		
		model.addConstr(gp.quicksum(zr[0,j] for j in range(N)) +l[0]==1)

			
			
		model.addConstrs(gp.quicksum(zr[i,t-1] for i in range(0,t)) == gp.quicksum(
			 zr[t,j]  for j in  range(t,N)) + l[t] for t in range(1,N))       
			
			
		model.addConstrs(gp.quicksum(zr[i,t] for i in range(0,t+1)) <= yr[t] for t in range(N))    
			

		model.addConstrs(gp.quicksum(SR[i][t]*zr[i,t] for i in range(t+1) ) ==
						  gp.quicksum(SD[t][j]*zsr[t,j] for j in range(t,N)) for t in range(N))


		model.addConstrs(gp.quicksum(SD[i][t]*zsp[i,t] for t in range(i,N)) <= yp[i]*min(C,SD[i][N-1]) for i in range(N))
		
		model.addConstrs(gp.quicksum(SD[i][t]*zsr[i,t] for t in range(i,N)) <= yr[i]*min(SR[0][i],SD[i][N-1]) for i in range(N))
		
		model.addConstrs((gp.quicksum(SD[t][k]*zsp[t,k] for k in range(t,N)) +
						   gp.quicksum(SD[t][k]*zsr[t,k] for k in range(t,N))<= C for t in range(N)))
		


		
	 

		# Parameters 
		model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
		model.setParam(GRB.Param.MIPGap, EPSILON)
		model.setParam(GRB.Param.Threads,1)
		model.setParam(GRB.Param.Cuts, -1)
		model.setParam(GRB.Param.Presolve,-1)




		# Optimize model
		model.optimize()




		print('Obj: %g' % model.ObjVal)

	except gp.GurobiError as e:
		print('Error code ' + str(e.errno) + ': ' + str(e))

	return model.ObjVal, model.ObjBound,model.MIPGap,model.Runtime, model.NodeCount