#!/bin/bash
#script para executar instancias cedidas por Sifarelas A.
#52 periodos, 108 instancias

opt=mip #lp ou mip
form=std
instance=sifa
fatorc=1.5 #1.5 1.75 2.0
description=${instance}_${form}_${fatorc}_${opt}

for tam in 52
do
    for id in $(seq 10)
       do
	        python3 main.py ${tam}_${id}.txt ${fatorc}
       done

done
