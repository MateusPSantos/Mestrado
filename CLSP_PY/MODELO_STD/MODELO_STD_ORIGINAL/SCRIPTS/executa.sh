#!/bin/bash
#script para executar instancias cedidas por Sifarelas A.
#52 periodos, 108 instancias

opt=mip #lp ou mip
form=std
instance=sifa
fatorc=1.5 #1.5 1.75 2.0
description=${instance}_${form}_${fatorc}_${opt}

for id in $(seq 108)
do
	python3 main.py c52_${id}.txt 
done
