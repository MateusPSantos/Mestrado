



def leitura_instance(file_name):
	arq = open(file_name)
	N = int(arq.readline())
	PP  = [0]*N
	PR  = [0]*N

	FP = [float(arq.readline())]*N
	FR = [float(arq.readline())]*N

	HR = [float(arq.readline())]*N
	HP = [float(arq.readline())]*N

	D = [int(i) for i in arq.readline().split()]
	
	R = [int(i) for i in arq.readline().split()]

	C = float(arq.readline().rstrip('\n'))
	
	return N, PP, PR, FP, FR, HR, HP, D, R, C