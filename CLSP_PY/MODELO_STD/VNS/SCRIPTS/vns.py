
import gurobipy as gp
from gurobipy import GRB


MAX_CPU_TIME = 3600.0
EPSILON = 0.000001

# nv : indice da geracao de vizinhanca
# periodo : periodo escolhido referência
def vns(yp_sol ,yr_sol,N, PP, PR, FP, FR, HR, HP, D, R, SD,SR,C,xp_sol,xr_sol,sp_sol,sr_sol,nv,periodo):



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

        if nv == 1:
            yp[periodo].lb = 1
            yp[periodo].ub = 1

            for i in range(periodo):
                model.addConstr(xp[i] <= xp_sol[i])
                model.addConstr(sp[i] <= sp_sol[i])

            for i in range(N):
                if i != periodo:
                    yp[i].lb = yp_sol[i]
                    yp[i].ub = yp_sol[i]
                if i >= periodo:
                    xp[i].lb = xp_sol[i]
                    xp[i].ub = xp_sol[i]
                    sp[i].lb = sp_sol[i]
                    sp[i].ub = sp_sol[i]
                yr[i].lb    = yr_sol[i]
                yr[i].ub    = yr_sol[i]
                sr[i].lb    = sr_sol[i]
                sr[i].ub    = sr_sol[i]
                xr[i].lb    = xr_sol[i]
                xr[i].ub    = xr_sol[i]

        elif nv == 2:
            yp[periodo].lb = 0
            yp[periodo].ub = 0

            for i in range(periodo):
                model.addConstr(xp[i] >= xp_sol[i])
                model.addConstr(sp[i] >= sp_sol[i])

            for i in range(N):
                if i != periodo:
                    yp[i].lb    = yp_sol[i]
                    yp[i].ub    = yp_sol[i]
                if i >= periodo:
                    xp[i].lb   = xp_sol[i]
                    xp[i].ub   = xp_sol[i]
                    sp[i].lb   = sp_sol[i]
                    sp[i].ub   = sp_sol[i]
                yr[i].lb    = yr_sol[i]
                yr[i].ub    = yr_sol[i]
                sr[i].lb    = sr_sol[i]
                sr[i].ub    = sr_sol[i]
                xr[i].lb    = xr_sol[i]
                xr[i].ub    = xr_sol[i]

        elif nv == 3:
            yr[periodo].lb = 1
            yr[periodo].ub = 1

            for i in range(N):
                model.addConstr(sr[i] < sr_sol[i])
                model.addConstr(sp[i] >= sp_sol[i])

            for i in range(N):
                if i != periodo:
                    yr[i].lb    = yr_sol[i]
                    yr[i].ub    = yr_sol[i]
                    xr[i].start = xr_sol[i]
                yp[i].lb    = yp_sol[i]
                yp[i].ub    = yp_sol[i]
                xp[i].start    = xp_sol[i]
        elif nv == 4:

            yr[periodo].lb = 1
            yr[periodo].ub = 1

            for i in range(N):
                model.addConstr(sr[i] < sr_sol[i])
                model.addConstr(sp[i] < sp_sol[i])
                model.addConstr(xp[i] < xp_sol[i])

            for i in range(N):
                if i != periodo:
                    yr[i].lb    = yr_sol[i]
                    yr[i].ub    = yr_sol[i]
                    xr[i].start = xr_sol[i]
                yp[i].lb    = yp_sol[i]
                yp[i].ub    = yp_sol[i]

        elif nv == 5:
            yr[periodo].lb = 0
            yr[periodo].ub = 0

            model.addConstrs(sr[i] > sr_sol[i] for i in range(N))

            for i in range(N):
                if i != periodo:
                    yr[i].lb    = yr_sol[i]
                    yr[i].ub    = yr_sol[i]
                sp[i].start = sp_sol[i]
                xp[i].start = xp_sol[i]
                xr[i].start = xr_sol[i]
                yp[i].lb    = yp_sol[i]
                yp[i].ub    = yp_sol[i]

        elif nv == 6 :
            




      
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
            sp[i].start = sp_sol[i]
            sr[i].start = sr_sol[i]


        
        model.update()
        # # Set objective
        model.setObjective(gp.quicksum(PP[i]*xp[i]+sp[i]*HP[i] + xr[i]*PR[i] + sr[i]*HR[i] + yp[i]*FP[i] + yr[i]*FR[i] for i in range(N)) , sense = GRB.MINIMIZE)

        # # Add constraints
    
        model.addConstr(xp[0]+xr[0]-sp[0] == D[0])
        model.addConstrs(sp[i-1] + xp[i] + xr[i] - sp[i] == D[i] for i in range(N) if i > 0 )
        model.addConstr(R[0] - xr[0] - sr[0] == 0)
        model.addConstrs(sr[i-1] + R[i] - xr[i] - sr[i] == 0 for i in range(N) if i > 0)
        model.addConstrs(xp[i] - yp[i]*min(C,SD[i][N-1]) <= 0 for i in range(N))
        model.addConstrs(xr[i] - yr[i]*min(SR[0][i], SD[i][N-1],C) <= 0 for i in range(N))
        model.addConstrs(xp[i] + xr[i] <= C for i in range(N))
       # model.write(file_name+"_model.lp")

        # Parameters 
        model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
        model.setParam(GRB.Param.MIPGap, EPSILON)
        model.setParam(GRB.Param.Threads,3)
        model.setParam(GRB.Param.Cuts, -1)
        model.setParam(GRB.Param.Presolve,-1)



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

    return model.ObjVal, xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol, model.ObjBound, model.NodeCount,model.MIPGap,model.Runtime
