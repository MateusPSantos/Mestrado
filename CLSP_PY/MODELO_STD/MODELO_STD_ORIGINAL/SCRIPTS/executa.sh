#!/bin/bash
#52 periodos, 108 instancias

fo=std

# set01 {1..12}
# set02 {13..24}
# set03 {25..36}
# set04 {37..48}
# set05 {49..60}
# set06 {61..72}
# set07 {73..84}
# set08 {85..96}
# set09 {97..108}

for id in {1..12} # in $(seq 1)
do
	python3 main.py c52_${id}.txt >> report/out_${fo}_c52_${id}.txt
done
