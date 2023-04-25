import gurobipy as gp
from gurobipy import GRB
import numpy as np

#######################################################################
###                    PARAMETROS                                  ###    
######################################################################

MAX_CPU_TIME = 3600.0
EPSILON = 0.000001
cap = True

lsdbar = 1

#######################################################################
###                    MODELO			                           ###    
######################################################################

def clsr_mc(N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,xp_sol,xr_sol,yp_sol,yr_sol,wp_sol,wr_sol,vor_sol):

	CP = [0]*N
	CR = [0]*N
	KP = 0
	KR = 0 

	for i in range(N):
		CP[i] = PP[i]

		for j in range(i,N):
			CP[i] = CP[i] + HP[j]

#	for l in range(0,N):
#		if l < 1:
#			rrl[l] = R[l]
#		else:
#			rrl[l] = R[l] + max(0.0, rrl[l-1]-D[l-1])
#
#		dl[l] = max(0.0,D[l]-rrl[l])

#	for k in range(0,N):
#		sdl[k][k] = dl[k]
#		for j in range(k+1,N):
#			sdl[k][j] = sdl[k][j-1] + dl[j]
#
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

		for i in range(N):
			xp[i].start = xp_sol[i]
			xr[i].start = xr_sol[i]
			yp[i].start = yp_sol[i]
			yr[i].start = yr_sol[i]
			for j in range(i,N):
				wp[i,j].start  = wp_sol[i][j]
				wr[i,j].start  = wr_sol[i][j]
				vor[i,j].start = vor_sol[i][j]

		model.update()

		# # Set objective
		FO = 0.0
		#FO = gp.quicksum(xp[i]*CP[i] for i in range(N)) + gp.quicksum(yp[i]*FP[i] for i in range(N)) \
		#	+ gp.quicksum(xr[i]*CR[i] for i in range(N)) + gp.quicksum(yr[i]*FR[i] for i in range(N)) + K

		for i in range(N):
			FO+= xp[i]*CP[i]

		for i in range(N):
			FO+= yp[i]*FP[i]

		for i in range(N):
			FO+= xr[i]*CR[i]

		for i in range(N):
			FO+= yr[i]*FR[i]

		FO+= K
		
		model.setObjective(FO, sense = GRB.MINIMIZE)

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

		# # Add constraints

		#model.addConstrs(gp.quicksum(wp[j,i]+wr[j,i] for j in range(i+1)) >= D[i] for i in range(N))

		#model.addConstrs(gp.quicksum(vor[j,i] for j in range(i+1)) + gp.quicksum((-wr[i,j]) for j in range(i,N))
		#							>= 0 for i in range(N)
		#							)

		#model.addConstrs(gp.quicksum(vor[i,j] for j in range(i,N)) <= R[i] for i in range(N))

		#model.addConstrs(wp[i,j] <= yp[i]*D[j]  for i in range(N) for j in range(i,N) )

		#model.addConstrs(wr[i,j] <= min(SR[0][i],D[i])  for j in range(i,N) for i in range(N) )

		#model.addConstrs(vor[i,j] + yr[j]*(-R[i])  <= 0 for j in range(i,N) for i in range(N))

		#model.addConstrs(xp[i]+ gp.quicksum((-wp[i,j]) for j in range(i,N)) == 0 for i in range(N))

		#model.addConstrs(xr[i]+ gp.quicksum((-wr[i,j]) for j in range(i,N)) == 0 for i in range(N))

		#model.addConstrs(xp[i] - yp[i]*min(C,SD[i][N-1]) <= 0 for i in range(N))
		#model.addConstrs(xr[i] - yr[i]*min(SR[0][i], SD[i][N-1]) <= 0 for i in range(N))

		#model.addConstrs(xp[i]+xr[i] <= C for i in range(N))

		#if lsdbar == 1:
		#	model.addConstrs((gp.quicksum(xp[l] for l in range(i))+ gp.quicksum(yp[l]*sdl[l][j] for l in range(i,j+1))) >= sdl[0][j] for i in range(N) for j in range(i,N))

		# Parameters 
		model.setParam(GRB.Param.TimeLimit,MAX_CPU_TIME)
		model.setParam(GRB.Param.MIPGap,EPSILON)
		model.setParam(GRB.Param.Threads,1)
		#model.setParam(GRB.Param.Cuts,-1)
		#model.setParam(GRB.Param.Presolve,-1)

		# Optimize model
		model.optimize()

		tmp=0
		if model.status == GRB.OPTIMAL:
			tmp=1

		print('Obj: %g' % model.ObjVal)

	except gp.GurobiError as e:
		print('Error code ' + str(e.errno) + ': ' + str(e))

	return model.ObjVal,model.ObjBound,model.MIPGap,model.Runtime,model.NodeCount,tmp