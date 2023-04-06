#!/bin/bash
#52 periods, 108 instances

for fo in STD #MC SP STD
do
	cd ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS
	bash execute_${fo}.sh
done
