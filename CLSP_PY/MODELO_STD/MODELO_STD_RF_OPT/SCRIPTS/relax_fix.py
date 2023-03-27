


import gurobipy as gp
from gurobipy import GRB

MAX_CPU_TIME = 3600.0
EPSILON = 0.000001


def relax_fix(particoes,yp_sol ,yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C):

	xp_sol1 = [0]*N
	xr_sol1 = [0]*N
	sp_sol1 = [0]*N
	sr_sol1 = [0]*N
	yp_sol1 = [0]*N
	yr_sol1 = [0]*N

	objval = 0.0
	bestbound = 0.0
	numnode = 0.0
	elapsed = 0.0
	gap = 0.0

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


		
	
		xp_sol1 = [xp[i].X for i in range(N)]
		xr_sol1 = [xr[i].X for i in range(N)]
		sp_sol1 = [sp[i].X for i in range(N)]
		sr_sol1 = [sr[i].X for i in range(N)]
		yp_sol1 = [yp[i].X for i in range(N)]
		yr_sol1 = [yr[i].X for i in range(N)]


	except gp.GurobiError as e:
		print('Error code ' + str(e.errno) + ': ' + str(e))

	#except AttributeError:
	#	print('Encountered an attribute error')

	return model.ObjVal, xp_sol1,xr_sol1,sp_sol1,sr_sol1, yp_sol1,yr_sol1, bestbound, numnode, gap,elapsed
