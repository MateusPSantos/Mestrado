
import gurobipy as gp
from gurobipy import GRB

MAX_CPU_TIME = 3600.0
EPSILON = 0.000001

def fix_and_optimize(particoes,yp_sol ,yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,xp_sol,xr_sol,wp_sol,wr_sol,vor_sol):

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
			if i not in particoes:
				yp[i].lb    = yp_sol[i]
				yp[i].ub    = yp_sol[i]
				yr[i].lb    = yr_sol[i]
				yr[i].ub    = yr_sol[i]
			else:
				yp[i].start = yp_sol[i]
				yr[i].start = yr_sol[i]
		for i in range(N):
			xp[i].start = xp_sol[i]
			xr[i].start = xr_sol[i]
			for j in range(i,N):
				wp[i,j].start  = wp_sol[i][j]
				wr[i,j].start  = wr_sol[i][j]
				vor[i,j].start = vor_sol[i][j]
		
		model.update()
		# # Set objective
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
		# Parameters 
		model.setParam(GRB.Param.TimeLimit,MAX_CPU_TIME)
		model.setParam(GRB.Param.MIPGap,EPSILON)
		model.setParam(GRB.Param.Threads,1)
		#model.setParam(GRB.Param.Cuts,-1)
		#model.setParam(GRB.Param.Presolve,-1)

		# Optimize model
		model.optimize()

		xp_sol  = [xp[i].X for i in range(N)]
		xr_sol  = [xr[i].X for i in range(N)]
		for i in range(N):
			for j in range(i,N):
				wp_sol[i][j] = wp[i,j].X
				wr_sol[i][j] = wr[i,j].X
				vor_sol[i][j] = vor[i,j].X
		yp_sol  = [yp[i].X for i in range(N)]
		yr_sol  = [yr[i].X for i in range(N)]

		print('Obj: %g' % model.ObjVal)

	except gp.GurobiError as e:
		print('Error code ' + str(e.errno) + ': ' + str(e))

	return model.ObjVal,xp_sol,xr_sol,wp_sol,wr_sol,vor_sol,yp_sol,yr_sol,model.ObjBound,model.NodeCount,model.MIPGap,model.Runtime
