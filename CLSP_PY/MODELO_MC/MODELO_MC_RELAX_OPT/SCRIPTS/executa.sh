#!/bin/bash
#52 periodos, 108 instancias

fo=mc

for id in $(seq 1)
do
	python3 main.py c52_${id}.txt >> report/out_${fo}_c52_${id}.txt
done
