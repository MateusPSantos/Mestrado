#include "cabecalho.h"

int main (int argc, char *argv[]) {
  double *HP, *HR, *PP, *FP, *PR, *FR, *D, *R;
  double setup;
  double KP, KR, AUX;
  register int i, j, k, t, l;
  FILE* fp;
  double objval;  
  FILE* fpout;
  time_t start, end;
   
  /*instance*/
  opc.instance_sifaleras = 0;
  opc.instance_mathijn = 0;

  N = 0;
  objval = 0.0;
  numnode = 0;
  bestbound = 0.0;
  elapsed = 0;
  setup = 0.0;
  gap = 0.0;
  status = 0;
  
  if (argc < 1 || argc > 10) {
    printf("numero de parametros de entrada errado \n");
    return 0;
  }
  
  fp = fopen(argv[1], "r");
  if (fp == NULL) {
    fprintf(stderr, "nao pode abrir %s \n", argv[1]);
    return 0;
  }
  
  for (i=2; i<argc; i++) {
    if (strcmp(argv[i], "-isifa") == 0) {
      opc.instance_sifaleras = 1;
    } else if (strcmp(argv[i], "-imath") == 0) {
      opc.instance_mathijn = 1;
    } else if (opc.instance_mathijn == 1 && N==0) {
      N = atoi(argv[i]);
    } else if (opc.instance_mathijn == 1 && N!=0) {
      setup = atoi(argv[i]);
    } else {
      printf("parametros de entrada errado \n");
    }
  }
  
  if (opc.instance_sifaleras == 1) {
    if (fscanf(fp, "%d", &N) != 1) {
      fprintf(stderr, "error : falta entrada  \n");
      exit(1);
    }
  }
  
  HP = calloc_vetor_double(N);
  PP = calloc_vetor_double(N);
  FP = calloc_vetor_double(N);
  HR = calloc_vetor_double(N);
  PR = calloc_vetor_double(N);
  FR = calloc_vetor_double(N);
  D = calloc_vetor_double(N);
  R = calloc_vetor_double(N);
  SD = calloc_matriz_double(N,N);
  SR = calloc_matriz_double(N,N);
  CP = calloc_vetor_double(N);
  CR = calloc_vetor_double(N);
  rrl = calloc_vetor_double(N);
  dl = calloc_vetor_double(N);
  sdl = calloc_matriz_double(N, N);
  
  lerdados (fp, HP, PP, FP, HR, PR, FR, D, R, setup);
  
  fclose(fp);
  fp = NULL;
  
  /*
    printf("N = %d \n", N);
    printf("HP = [ ");
    for (i=0; i<N; i++) printf("%d ", HP[i]); printf("] \n"); 
    printf("PP = [ "); for (i=0; i<N; i++) printf("%.2f ", PP[i]); printf("] \n");
    printf("FP = [ "); for (i=0; i<N; i++) printf("%.2f ", FP[i]); printf("] \n");
    printf("HR = [ "); for (i=0; i<N; i++) printf("%.2f ", HR[i]); printf("] \n");
    printf("PR = [ "); for (i=0; i<N; i++) printf("%.2f ", PR[i]); printf("] \n");
    printf("D = [ "); for (i=0; i<N; i++) printf("%.2f ", D[i]); printf("] \n");
    printf("R = [ "); for (i=0; i<N; i++) printf("%.2f ", R[i]); printf("] \n");
  */
  
  for (i=0; i<N; i++) {
    SD[i][i] = D[i];
    SR[i][i] = R[i];
    for (j=i+1; j<N; j++) {
      SD[i][j] = SD[i][j-1] + D[j];
      SR[i][j] = SR[i][j-1] + R[j];
    }
  }
  
  for (i=0; i<N; i++) {
    CP[i] = PP[i];
    for (j=i; j<N; j++) CP[i] += HP[j];
  }
  
  for (l=0; l<N; l++) {    
    if (l<1) rrl[l] = R[l];
    else rrl[l] = R[l] + max(0.0, rrl[l-1]-D[l-1]);
    
    dl[l] = max(0.0, D[l]-rrl[l]);
  }
  
  for (k=0; k<N; k++) {
    sdl[k][k] = dl[k];
    for (j=k+1; j<N; j++) sdl[k][j] =  sdl[k][j-1] + dl[j];
  }
  
  for (i=0; i<N; i++) {
    CR[i] = PR[i];
    for (j=i; j<N; j++) CR[i] += HP[j];
    for (j=i; j<N; j++) CR[i] -= HR[j];
  }
  
  KP = 0;
  for (i=0; i<N; i++) {
    AUX = 0;
    for (j=0; j<=i; j++) AUX += D[j];
    KP += HP[i] * AUX;
  }
  
  KR = 0;
  for (i=0; i<N; i++) {
    AUX = 0;
    for (j=0; j<=i; j++) AUX += R[j];
    KR += HR[i] * AUX;
  }
  
  K = KR - KP;
  
  //printf("KP = %.2f, KR = %.2f, K = %.2f \n", KP, KR, K);

  /* model and solve the problem */
  objval = optimization(CP,CR,FP,FR,D,R);
  
  /*
    printf("solucao = %.2f \n", solucao);
    printf("xp = [ ");  for (i=0; i<N; i++) printf("%.2f ", x[i]); printf(" ]\n");
    printf("yp = [ ");  for (i=0; i<N; i++) printf("%.2f ", x[i+N]); printf(" ]\n");
    printf("xr = [ ");  for (i=0; i<N; i++) printf("%.2f ", x[i+2*N]); printf(" ]\n");
    printf("yr = [ ");  for (i=0; i<N; i++) printf("%.2f ", x[i+3*N]); printf(" ]\n");
  */
  
  fpout = fopen ("table.txt", "a");
  fprintf (fpout,"%s;%.1f;%.1f;%.1f;%d;%d;%d \n",argv[1],objval,bestbound,gap,numnode,elapsed,status);
  fclose (fpout);
  
  free_vetor_double(HP);
  free_vetor_double(PP);
  free_vetor_double(FP);
  free_vetor_double(HR);
  free_vetor_double(PR);
  free_vetor_double(FR);
  free_vetor_double(D);
  free_vetor_double(R);
  free_matriz_double(N, SD);
  free_matriz_double(N, SR);
  free_vetor_double(CP);
  free_vetor_double(CR);
  free_vetor_double(rrl);
  free_vetor_double(dl);
  free_matriz_double(N, sdl);
  free_vetor_double(x);
   
  return 0;
  
}
