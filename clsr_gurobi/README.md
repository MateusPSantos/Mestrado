# clsr_gurobi
Capacitated lot sizing problem with return

Capacitated
$$
soma = \sum_{i=1}^{n} d_i
$$

C = (soma*fator)/n

onde fator é 1.5, 1.75 ou 2.0

- Recompile the C++ library for the API and replace the old one to resolve any ABI incompatibilities.
cd /opt/gurobi910/linux64/src/build
make
cp libgurobi_c++.a ../../lib/
