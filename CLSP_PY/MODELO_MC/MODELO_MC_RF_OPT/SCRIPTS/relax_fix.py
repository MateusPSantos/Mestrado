


import gurobipy as gp
from gurobipy import GRB
import numpy as np
MAX_CPU_TIME = 3600.0
EPSILON = 0.000001


def relax_fix(particoes,yp_sol ,yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C):

	xp_sol1 = [0]*N
	xr_sol1 = [0]*N
	wp_sol1 = (np.zeros((N,N))).tolist()
	wr_sol1 = (np.zeros((N,N))).tolist()
	vor_sol1 = (np.zeros((N,N))).tolist()
	yp_sol1 = [0]*N
	yr_sol1 = [0]*N

	objval = 0.0
	bestbound = 0.0
	numnode = 0.0
	elapsed = 0.0
	gap = 0.0

	CP = [0]*N
	CR = [0]*N
	KP = 0
	KR = 0 

	for i in range(N):
		CP[i] = PP[i]

		for j in range(i,N):
			CP[i] = CP[i] + HP[j]

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
		wr   = model.addVars([(i,j) for i in range(N) for j in range(i,N)], lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="wr")
		vor  = model.addVars([(i,j) for i in range(N) for j in range(i,N)],lb =0.0, ub = float('inf'),vtype=GRB.CONTINUOUS, name="vor")
		xp    = model.addVars(list(range(N)), lb = 0.0, ub = float('inf'), vtype=GRB.CONTINUOUS, name="xp")
		xr    = model.addVars(list(range(N)), lb = 0.0, ub = float('inf'), vtype=GRB.CONTINUOUS, name="xr")
		yp   = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.BINARY, name="yp")
		yr   = model.addVars(list(range(N)), lb = 0.0, ub = 1.0, vtype=GRB.BINARY, name="yr")
		
		for i in range(N):
			if i > max(particoes) :
				yp[i].VType = gp.GRB.CONTINUOUS
				yp[i].lb    = 0
				yp[i].ub    = 1
				yr[i].VType = gp.GRB.CONTINUOUS
				yr[i].lb    = 0
				yr[i].ub    = 1
			elif i in particoes:
				yp[i].VType = gp.GRB.BINARY
				yp[i].lb = 0
				yp[i].ub = 1
				yr[i].VType = gp.GRB.BINARY
				yr[i].lb = 0
				yr[i].ub = 1
			else:
				yp[i].lb = yp_sol[i]
				yp[i].ub = yp_sol[i]
				yr[i].lb = yr_sol[i]
				yr[i].ub = yr_sol[i]

		
		model.update()

		# # Set objective
		FO = 0.0
		#FO = gp.quicksum(xp[i]*CP[i] for i in range(N)) + gp.quicksum(yp[i]*FP[i] for i in range(N)) \
		#   + gp.quicksum(xr[i]*CR[i] for i in range(N)) + gp.quicksum(yr[i]*FR[i] for i in range(N)) + K
		
		

		for i in range(N):
			FO+= xp[i]*CP[i]

		for i in range(N):
			FO+= yp[i]*FP[i]

		for i in range(N):
			FO+= xr[i]*CR[i]

		for i in range(N):
			FO+= yr[i]*FR[i]

		FO+= K

		# # Add constraints
		model.setObjective(FO, sense = GRB.MINIMIZE)
		# # Add constraints
	
		for i in range(N):
			ctr = 0.0
			for j in range(i+1):
				ctr += wp[j,i]
				ctr += wr[j,i]
			model.addConstr(ctr >= D[i])

		for i in range(N):
			ctr = 0.0
			for j in range(i+1):
				ctr+= vor[j,i]
			for j in range(i,N):
				ctr+=(-wr[i,j])
			model.addConstr(ctr == 0)

		for i in range(N):
			ctr =0.0
			for j in range(i,N):
				ctr += vor[i,j]
			model.addConstr(ctr <= R[i])

		for i in range(N):
			for j in range(i,N):
				model.addConstr(wp[i,j] + yp[i]*(-D[j]) <=0)


		for i in range(N):
			for j in range(i,N):
				model.addConstr(wr[i,j] + yr[i]*(-min(SR[0][i],D[j])) <=0)

		for i in range(N):
			for j in range(i,N):
				model.addConstr(vor[i,j] + yr[j]*(-R[i]) <= 0)

		for i in range(N):
			ctr = 0.0 
			ctr += xp[i]
			for j in range(i,N):
				ctr += (-wp[i,j])
			model.addConstr(ctr == 0)

		for i in range(N):
			ctr = 0.0
			ctr += xr[i]
			for j in range(i,N):
				ctr += (-wr[i,j])
			model.addConstr(ctr == 0)

#		model.addConstrs(
#			xp[i] - yp[i]*min(C,SD[i][N-1]) <= 0 for i in range(N)
#			)

#		model.addConstrs(
#			xr[i] - yr[i]*min(SR[0][i],SD[i][N-1],C) <= 0 for i in range(N)
#			)

		model.addConstrs(
			xp[i] + xr[i] <= C for i in range(N)
			)
		#model.write(file_name+".lp")

		# Parameters 
		model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
		model.setParam(GRB.Param.MIPGap, EPSILON)
		model.setParam(GRB.Param.Threads,1)
		model.setParam(GRB.Param.Cuts, -1)
		model.setParam(GRB.Param.Presolve,-1)


		# Optimize model
		model.optimize()


		objval = model.ObjVal
		bestbound = model.ObjBound
		numnode = model.NodeCount
		elapsed = model.Runtime
		gap = model.MIPGap


		
	
		xp_sol1  = [xp[i].X for i in range(N)]
		xr_sol1  = [xr[i].X for i in range(N)]
		for i in range(N):
			for j in range(i,N):
				wp_sol1[i][j] = wp[i,j].X
				wr_sol1[i][j] = wr[i,j].X
				vor_sol1[i][j] = vor[i,j].X
		yp_sol1  = [yp[i].X for i in range(N)]
		yr_sol1  = [yr[i].X for i in range(N)]


	except gp.GurobiError as e:
		print('Error code ' + str(e.errno) + ': ' + str(e))

	#except AttributeError:
	#	print('Encountered an attribute error')

	return model.ObjVal, xp_sol1,xr_sol1,wp_sol1,wr_sol1, vor_sol1,yp_sol1,yr_sol1, bestbound, numnode, gap,elapsed
