

def gera_particoes(N,semente = 42,tamanho_particao=3,indice_geracao = 1):
	subset = []
     
	if indice_geracao == 1:
		for i in range(0,N,tamanho_particao):
			if i + tamanho_particao > N:
				subset.append([k for k in range(i,N)])
			else:
				subset.append([k for k in range(i,i+tamanho_particao)])
	else:
		from random import sample
		import random
		random.seed(semente)
		lista_periodos = [k  for k in range(N)]
		while True:
             
			sub_conj = []
             
			if len(lista_periodos) >= tamanho_particao:
				sub_conj = sample(lista_periodos,tamanho_particao)
			else:
				sub_conj = lista_periodos[:]
			subset.append(sub_conj)
			for i in sub_conj:
				lista_periodos.remove(i)
			if len(lista_periodos)==0:
				break
	return subset