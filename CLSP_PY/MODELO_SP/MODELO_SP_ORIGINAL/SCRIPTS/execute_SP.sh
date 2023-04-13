#!/bin/bash
#52 periodos, 108 instancias

prob=clsr
fo=sp
solver=mip

# set01 {1..12}
# set02 {13..24}
# set03 {25..36}
# set04 {37..48}
# set05 {49..60}
# set06 {61..72}
# set07 {73..84}
# set08 {85..96}
# set09 {97..108}

for id in {73..84} #$(seq 1)
do
	python3 ${prob}_${fo}_${solver}.py c52_${id}.txt >> report/out_${prob}_${fo}_${solver}_c52_${id}.txt
done
