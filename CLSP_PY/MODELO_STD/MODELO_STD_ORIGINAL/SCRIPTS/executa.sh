#!/bin/bash
#52 periodos, 108 instancias

for id in $(seq 108)
do
	python3 main.py c52_${id}.txt 
done
