
import gurobipy as gp
from gurobipy import GRB
import numpy as np

#######################################################################
###                    PARAMETROS                                  ###    
######################################################################



MAX_CPU_TIME = 3600.0
EPSILON = 0.000001
cap = True





#######################################################################
###                    MODELO			                           ###    
######################################################################


def clsr_mc(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C):


	CP = [0]*N
	CR = [0]*N
	rrl = [0]*N
	dl = [0]*N
	sdl = (np.zeros(N,N)).tolist()
	KP = 0
	KR = 0 

	for i in range(N):
		CP[i] = PP[i]

		for j in range(i,N):
			CP[i] = CP[i] + HP[j]

	for l in range(0,N):
		if l < 1:
			rrl[l] = R[l]
		else:
			rrl[l] = R[l] + max(0.0, rrl[l-1]-D[l-1])

		dl[l] = max(0.0,D[l]-rrl[l])

	for k in range(0,N):
		sdl[k][k] = dl[k]
		for j in range(k+1,N):
			sdl[k][j] = sdl[k][j-1] + dl[j]

	for i in range(N):
		CR[i] = PR[i]
		for j in range(i,N):
			CR[i] += HP[j]
		for j in range(i,N):
			CR[i] -= HR[j]


	
	


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


		# # Set objective
		FO = None
		for i in range(N):
			FO += yp[i]*FP[i] + yr[i]*FR[i] + l[i]*CL[i] + gp.quicksum(zsp[i,j]*CSP[i][j] + zsr[i,j]*CSR[i][j]+
																	   zr[i,j]*CR[i][j] for j in range(i,N))

		
		model.setObjective(FO, sense = GRB.MINIMIZE)

		# # Add constraints

		# # Set objective
		FO = None
		for i in range(N):
			FO += yp[i]*FP[i] + yr[i]*FR[i] + l[i]*CL[i] 
			
			for j in range(i,N):
				FO+=zsp[i,j]*CSP[i][j] + zsr[i,j]*CSR[i][j]+zr[i,j]*CR[i][j] 

		model.setObjective(FO, sense = GRB.MINIMIZE)

		# # Add constraints
		model.setObjective(FO, sense = GRB.MINIMIZE)

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
