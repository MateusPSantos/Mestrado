import gurobipy as gp
from gurobipy import GRB
from pathlib import Path
import os
import numpy as np
import sys
import random as rd



def main():

    #######################################################################
    ###                    PARAMETROS                                  ###    
    ######################################################################

	
    cap = True
    file_name = sys.argv[1]

    MAX_CPU_TIME = 600.0
    EPSILON = 0.000001

    
    INSTANCE_PATH = Path('../instances/sifaleras')
    RESULT_PATH   = Path('../RESULTADOS/')




    #######################################################################
    ###                    LEITURA                                     ###    
    ######################################################################

    def leitura_instance(file_name):
        arq = open(os.path.join(INSTANCE_PATH,file_name))
        N = int(arq.readline())
        PP  = [0]*N
        PR  = [0]*N

        FP = [float(arq.readline())]*N
        FR = [float(arq.readline())]*N

        HR = [float(arq.readline())]*N
        HP = [float(arq.readline())]*N

        D = [int(i) for i in arq.readline().split()]
    
        R = [int(i) for i in arq.readline().split()]
    
        return N, PP, PR, FP, FR, HR, HP, D, R


    N, PP, PR, FP, FR, HR, HP, D, R =leitura_instance(file_name)


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
    gap = 0

    #######################################################################
    ###                    HEURISTICAS                                 ###    
    ######################################################################


    def gera_particoes(N,tamanho_particao=3):
        subset = []

        tam_subset = tamanho_particao

        for i in range(0,N,tam_subset):
            if i + tam_subset > N:
                subset.append([k for k in range(i,N)])
            else:
                subset.append([k for k in range(i,i+tam_subset)])
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

            
            model.write(file_name+".lp")

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



    
    




    '''
    *********************************************************************
    ***                FIX AND OPTIMIZE                               ***
    *********************************************************************
    '''



    def fix_and_optimize(particoes,yp_sol ,yr_sol):

        indices = []

        if len(particoes) == 1 :
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
            model.write(file_name+"_model.lp")

            # Parameters 
            model.setParam(GRB.Param.TimeLimit, MAX_CPU_TIME)
            model.setParam(GRB.Param.MIPGap, EPSILON)
            model.setParam(GRB.Param.Threads,1)
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

        return model.ObjVal, xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol


    '''
    *********************************************************************
    ***                LOCAL SEARCH HEURISTIC                         ***
    *********************************************************************
    '''



    def heuristic():
    
        for particao in subset:
            obj,xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol = relax_fix(particao,yp_sol,yr_sol)
        
        for particao in subset:
            obj,xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol = fix_and_optimize(particao,yp_sol,yr_sol)
        
        obj_    = obj
        xp_sol_ = xp_sol.copy()
        xr_sol_ = xr_sol.copy()
        sp_sol_ = sp_sol.copy()
        sr_sol_ = sr_sol.copy()
        yp_sol_ = yp_sol.copy()
        yr_sol_ = yr_sol.copy()


        
        for cont in range(30):
            part_sort = rd.randint(0,len(subset)-1)

            obj_,xp_sol_,xr_sol_,sp_sol_,sr_sol_, yp_sol_,yr_sol_ = fix_and_optimize(subset[part_sort],yp_sol_,yr_sol_)

            if obj_ < obj :
                obj = obj_
                xp_sol = xp_sol_.copy()
                xr_sol = xr_sol_.copy()
                sp_sol = sp_sol_.copy()
                sr_sol = sr_sol_.copy()
                yp_sol = yp_sol_.copy()
                yr_sol = yr_sol_.copy()
        

        return obj,xp_sol,xr_sol, sp_sol,sr_sol, yp_sol,yr_sol

        
        

    ###########################################################################
    ###                  CHAMA FUNÇÕES                                      ###
    ###########################################################################




	#obj,xp_sol,xr_sol, sp_sol,sr_sol, yp_sol,yr_sol = heuristic()
    for particao in subset:
            obj,xp_sol,xr_sol,sp_sol,sr_sol, yp_sol,yr_sol,bestbound,numnode, gap = relax_fix(particao,yp_sol,yr_sol)


    arquivo = open('relax_fix_'+file_name,'a')
    arquivo.write(file_name+';'+str(round(obj,3))+';'+str(round(bestbound,3))+';'+str(round(numnode,3))+';'+str(round(gap,3)))
    arquivo.close()







if __name__== "__main__" :
	main()







