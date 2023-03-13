#!/bin/bash
#52 periodos, 108 instancias

fo=std

for id in $(seq 108)
do
	python3 main.py c52_${id}.txt >> saida.txt
	mv saida.txt report/out_${fo}_c52_${id}.txt
done
