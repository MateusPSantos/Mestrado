#!/bin/bash
#52 periodos, 108 instancias

fo=mc

for id in {1..108} #$(seq 1)
do
	python3 clsr_math_mc_mip.py c52_${id}.txt 6 3 >> report/out_${fo}_c52_${id}.txt
done
