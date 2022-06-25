#ifndef CABECALHO_H_INCLUDED
#define CABECALHO_H_INCLUDED

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "gurobi_c++.h"
#include "aloca.cpp"
#include <iostream>
#include <sstream>

#define MAX_CPU_TIME 3600
#define EPSILON 0.000001

using namespace std;

typedef struct opcoes {
  int instance_sifaleras, instance_mathijn;
} str_opc;

str_opc opc;

int N;
double **SD, **SR;
double *CP, *CR;
double *rrl, *dl, **sdl;
double K;
double *x;

int elapsed;
int numnode;
double bestbound;
double gap;
int status;

string IntToString (int a);

void lerdados (FILE *fp, double *HP, double *PP, double *FP, double *HR, double *PR, double *FR, double *D, double *R, double setup);
double optmization (double *CP, double *CR, double *FP, double *FR, double *D, double *R);

#include "lerdados.cpp"
#include "optimization.cpp"

#endif // CABECALHO_H_INCLUDED
