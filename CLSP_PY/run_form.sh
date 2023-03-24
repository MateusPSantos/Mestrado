#!/bin/bash
#52 periodos, 108 instancias

# set01 {1..12}
# set02 {13..24}
# set03 {25..36}
# set04 {37..48}
# set05 {49..60}
# set06 {61..72}
# set07 {73..84}
# set08 {85..96}
# set09 {97..108}

for fo in MC
do
	cd ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS
	bash execute_mc.sh
done

for fo in SP
do
	cd ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS
	bash execute_sp.sh
done

for fo in STD
do
	cd ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS
	bash execute_std.sh
done


#for fo in MC SP STD
#do
#	for id in {1..12} #$(seq 1)
#	do
#		python3 ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS/${prob}_${fo}_${solver}.py c52_${id}.txt >> ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTSreport/out_${prob}_${fo}_${solver}_c52_${id}.txt
#	done
#	cd ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS
#	bash executa.sh
#done
