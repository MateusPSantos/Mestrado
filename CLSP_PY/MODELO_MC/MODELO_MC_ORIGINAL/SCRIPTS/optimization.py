
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
	sdl = (np.zeros((N,N))).tolist()
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

	

	for i in range(N):
		AUX = 0 
		for j in range(i+1):
			AUX += D[j]

		KP += HP[i]*AUX

	for i in range(N):
		AUX = 0

		for j in range(i+1):
			AUX += R[j]

		KR += HR[i]*AUX

	K = KR - KP

	
	


	try:

		# Create a new model
		model = gp.Model("CLSR")

		# Create variables
		
		wp   = model.addVars([(i,j) for i in range(N) for j in range(i,N)], lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="wp")
		wr 	 = model.addVars([(i,j) for i in range(N) for j in range(i,N)], lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="wr")
		vor  = model.addVars([(i,j) for i in range(N) for j in range(i,N)],lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="vor")
		xp    = model.addVars(list(range(N)), lb = 0.0, ub = float('inf'), vtype=GRB.CONTINUOUS, name="xp")
		xr    = model.addVars(list(range(N)), lb = 0.0, ub = float('inf'), vtype=GRB.CONTINUOUS, name="xr")
		yp   = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.BINARY, name="yp")
		yr   = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.BINARY, name="yr")


		# # Set objective
		FO = None
		FO = gp.quicksum(xp[i]*CP[i] for i in range(N)) + gp.quicksum(yp[i]*FP[i] for i in range(N)) \
			+ gp.quicksum(xr[i]*CR[i] for i in range(N)) + gp.quicksum(yr[i]*FR[i] for i in range(N)) + K


		
		model.setObjective(FO, sense = GRB.MINIMIZE)

		

		# # Add constraints

		model.addConstrs(gp.quicksum(wp[j,i]+wr[j,i] for j in range(i+1)) >= D[i] for i in range(N))


		model.addConstrs(wp[i,j] <= yp[i]*D[j] for i in range(N) for j in range(i,N))


		model.addConstrs(xp[i]+ gp.quicksum((-wr[i,j]) for j in range(i,N)) == 0 for i in range(N))

		model.addConstrs(xp[i]+xr[i] <= C for i in range(N))


		model.addConstrs(gp.quicksum(vor[i,j] + yr[j]*(-R[i])for j in range(i,N)) <= 0 for i in range(N))

		model.addConstrs(gp.quicksum(vor[i,j] for j in range(i,N)) <= R[i] for i in range(N))

		model.addConstrs(gp.quicksum(vor[j,i] for j in range(i+1)) + gp.quicksum((-wr[i,j]) for j in range(i,N))
									>= 0 for i in range(N)
									)




		
	 

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
