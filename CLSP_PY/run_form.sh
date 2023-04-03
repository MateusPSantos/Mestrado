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

for fo in STD
do
	cd ~/repository/Mestrado/CLSP_PY/MODELO_${fo}/MODELO_${fo}_ORIGINAL/SCRIPTS
	bash execute_${fo}.sh
done
