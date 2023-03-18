#!/bin/bash
#52 periodos, 108 instancias

fo=std

# set01 {1..13}
# set02 {13..25}
# set03 {25..37}
# set04 {37..49}
# set05 {49..61}
# set06 {61..73}
# set07 {73..85}
# set08 {85..97}
# set09 {97..109}

for id in $(seq 1)
do
	python3 main.py c52_${id}.txt >> report/out_${fo}_c52_${id}.txt
done
