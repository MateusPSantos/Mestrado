#ifndef CABECALHO_H_INCLUDED
#define CABECALHO_H_INCLUDED

#include "gurobi_c++.h"
#include <cassert>
#include <cstdlib>
#include <cmath>
#include <sstream>
#include <fstream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "aloca.cpp"
#include <time.h>
#include <iostream>

#define MAX_CPU_TIME 3600.0
#define EPSILON 0.000001
#define INFTY 1000000000.0

using namespace std;

typedef struct opcoes {
  int solve_lp, solve_mip, instance_sifaleras, instance_mathijn;
} str_opc;

str_opc opc;

int N;
double **SD, **SR;

double *ssp, *sxp, *syp, *ssr, *sxr, *syr;

int elapsed;
int numnode;
double bestbound;
double gap;
int status;

string IntToString (int a);

void lerdados (FILE *fp, double *HP, double *PP, double *FP, double *HR, double *PR, double *FR, double *D, double *R, double setup);
double optimization (double *HP, double *PP, double *FP, double *HR, double *PR, double *FR, double *D, double *R, int *elapsed);

#include "lerdados.cpp"
#include "optimization.cpp"

#endif // CABECALHO_H_INCLUDED
