double optimization (double *CP, double *CR, double *FP, double *FR, double *D, double *R) {
  string varName;
  int lsdbar;
  double objval;
  time_t start, end;
  bool cap;
  int optimstatus;
  double soma;
  double fator;
  double Cap;
  
  lsdbar = 1;
  cap = true;
  
  soma = 0;
  for (int i=0; i<N; i++) {
    soma += D[i];
  }
  fator = 1.5; //1.5, 1.75, 2.0 
  Cap = (soma * fator)/N;
  
  try {
    
    //Create an environment
    GRBEnv env = GRBEnv(true);
    env.set("LogFile", "mip.log");
    env.start();
    
    //Create an empty model
    GRBModel model = GRBModel(env);
    
    /*VARIABLES*/
    GRBVar xp[N];
    GRBVar yp[N];
    GRBVar xr[N];
    GRBVar yr[N];
    
    for(int i=0; i < N; i++){
      xp[i]=model.addVar(0.0,GRB_INFINITY,0.0, GRB_CONTINUOUS,"xp("+IntToString(i)+")");
      yp[i]=model.addVar(0.0,1.0,0.0, GRB_INTEGER ,"yp("+IntToString(i)+")");
      xr[i]=model.addVar(0.0,GRB_INFINITY,0.0, GRB_CONTINUOUS,"xr("+IntToString(i)+")");
      yr[i]=model.addVar(0.0,1.0,0.0, GRB_INTEGER,"yr("+IntToString(i)+")");
    }
    
    GRBVar wp[N][N];
    for(int i=0; i< N; i++){
      for(int j=i;j<N; j++){
        wp[i][j]=model.addVar(0.0,GRB_INFINITY,0.0,GRB_CONTINUOUS,"wp("+IntToString(i)+")("+IntToString(j)+")");
      }
    }
    
    GRBVar wr[N][N];
    for(int i=0; i< N; i++){
      for(int j=i;j<N; j++){
        wr[i][j]=model.addVar(0.0,GRB_INFINITY,0.0,GRB_CONTINUOUS,"wr("+IntToString(i)+")("+IntToString(j)+")");
      }
    }
    
    GRBVar vor[N][N];
    for(int i=0; i< N; i++){
      for(int j=i;j<N; j++){
        vor[i][j]=model.addVar(0.0,GRB_INFINITY,0.0,GRB_CONTINUOUS,"vor("+IntToString(i)+")("+IntToString(j)+")");
      }
    }
    
    /*****OBJECTIVE******/
    GRBLinExpr obj = 0;
    obj += (K);  //XPRBaddterm(ctr, NULL, -K);
    for (int i=0; i<N; i++) obj += xp[i]*CP[i];
    for (int i=0; i<N; i++) obj += yp[i]*FP[i];
    for (int i=0; i<N; i++) obj += xr[i]*CR[i];
    for (int i=0; i<N; i++) obj += yr[i]*FR[i];
    
    model.setObjective(obj, GRB_MINIMIZE);
    
    /*****CONSTRAINTS*******/
    GRBLinExpr ctr;

    ctr = 0;
    for (int i=0; i<N; i++) {
      ctr = 0;
      for (int j=0; j<=i; j++) {
	ctr += wp[j][i];
	ctr += wr[j][i];
      }
      model.addConstr(ctr >= D[i]);  
    }
    
    /*
      for (int i=0; i<N; i++) {
      IloExpr ctr(env);
      for (int j=0 ; j<=i; j++) {
      for (int k=j; k<N; k++) {
      ctr += wr[j][k];
      }
      }
      model.add(ctr <= SR[0][i]);
      }
    */
    
    /*for (int i=0; i<N; i++) {
      for (int j=i; j<N; j++) {
	ctr = 0;
	ctr += wp[i][j]; 
	ctr += yp[i]*(-D[j]);
	model.addConstr(ctr <= 0);	
      }
    }*/

    for (int i = 0 ; i <N; i++){
      for (int j = i ; j  < N ; j++){
        model.addConstr(wp[i][j] <= D[j]*yp[i]);
      }
    }
    
 /*   for(int i=0; i < N; i++){
      ctr = 0;
      for(int j=i; j < N; j++){
	ctr += wp[i][j];
      }
      model.addConstr(ctr <= Cap * yp[i]);
    }*/

/*    for(int i=1; i < N; i++){
      ctr = 0;
      for(int j=0; j < i; j++){
  ctr += wp[j][i];
      }
      model.addConstr(ctr <= D[i]);
    }



    
    for (int i=0; i<N; i++) {
      for (int j=i; j<N; j++) {
	ctr = 0;
	ctr += wr[i][j];
	ctr += yr[i]*(-min(SR[0][i], D[j]));
	model.addConstr(ctr <= 0);
      }
    }*/
    
    for (int i=0; i<N; i++) {
      ctr = 0;
      ctr += xp[i];
      for (int j=i; j<N; j++)	{
	ctr += (-wp[i][j]);
      }
      model.addConstr(ctr == 0); 
    }
    
    for (int i=0; i<N; i++) {
      ctr = 0;
      ctr += xr[i];
      for (int j=i; j<N; j++)	{
	ctr += (-wr[i][j]);
      }
      model.addConstr(ctr == 0);
    }

    for (int i =0 ; i < N; i++){

      model.addConstr(xp[i]+xr[i] <= Cap);
    }


/*      for (int i=0; i < N; i++){

      model.addConstr(xp[i] <= min(Cap,SD[i][N-1])*yp[i]);
    }
  for (int i=0; i < N; i++){
      model.addConstr(xr[i] <= min(SR[0][i],SD[i][N-1])*yr[i]);
    }*/
    
    for (int i=0; i<N; i++) {
      for (int j=i; j<N; j++)	{
	ctr = 0;
	ctr += vor[i][j];
	ctr += yr[j]*(-R[i]);
	model.addConstr(ctr <= 0);
      }
    }
    
    for (int i=0; i<N; i++){
      ctr = 0;
      for(int j=i; j<N; j++) {
	ctr += vor[i][j];
      }
      model.addConstr(ctr <= R[i]);
    }
    
    for (int i=0; i<N; i++) {
      ctr = 0;
      for(int j=0; j<(i+1); j++) {
	ctr += vor[j][i];
      }		
      for(int j=i; j<N; j++) {
	ctr += (-wr[i][j]);
      }
      model.addConstr(ctr >= 0);
    }
    
    if (lsdbar == 1) { 
      for (int i=0;i<N;i++) {
	for (int j=i; j<N;j++) {
	  ctr=0;
	  for(int l=0;l<i;l++) {
	    ctr += xp[l];
	  }
	  for(int l=i;l<=j;l++) {
	    ctr += yp[l]*sdl[l][j];
	  }
	  model.addConstr(ctr >= sdl[0][j]);
	} 
      }
    }
    
    model.set(GRB_DoubleParam_TimeLimit, MAX_CPU_TIME);
    model.set(GRB_DoubleParam_MIPGap, EPSILON);
    model.set(GRB_IntParam_Threads, 3);
    model.set(GRB_IntParam_Cuts, 3);
    model.set(GRB_IntParam_Presolve, 1);
    
    /*solve the problem*/

    model.optimize();
    
    optimstatus = model.get(GRB_IntAttr_Status);

    objval = model.get(GRB_DoubleAttr_ObjVal);
    bestbound = model.get(GRB_DoubleAttr_ObjBound);
    numnode = model.get(GRB_DoubleAttr_NodeCount);
    elapsed = model.get(GRB_DoubleAttr_Runtime);
    gap = model.get(GRB_DoubleAttr_MIPGap);
    
    if (optimstatus == GRB_OPTIMAL) {
      status = 1;
    } else if (optimstatus == GRB_INF_OR_UNBD) {
      cout << "Model is infeasible or unbounded" << endl;
    } else if (optimstatus == GRB_INFEASIBLE) {
      cout << "Model is infeasible" << endl;
    } else if (optimstatus == GRB_UNBOUNDED) {
      cout << "Model is unbounded" << endl;
    } else {
      cout << "Optimization was stopped with status = " << optimstatus << endl;
    } 
    
  }
  catch (GRBException e){
    cout << "Error code = " << e.getErrorCode() << endl;
    cout << e.getMessage() << endl;
  }
  catch(...){
    
    cout << "Exception during optimization" << endl;
  }

  return objval;
  
}

string IntToString (int a) {
  ostringstream temp;
  temp<<a;
  return temp.str();
}
